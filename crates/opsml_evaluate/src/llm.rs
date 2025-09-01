use crate::error::EvaluationError;
use core::fmt::Debug;
use opsml_interfaces::llm::workflow::PyWorkflow;
use opsml_types::cards::LLMEvalMetric;
use opsml_utils::{
    create_uuid7, is_pydantic_model, json_to_pyobject_value, pyobject_to_json, PyHelperFuncs,
};
use potato_head::Score;
use potato_head::StructuredOutput;
use potato_head::TaskStatus;
use potato_head::Workflow;
use potato_head::WorkflowError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use tokio::task::JoinSet;
use tracing::{debug, error, instrument};

#[derive(Debug, Clone)]
#[pyclass]
pub struct EvalResult {
    #[pyo3(get)]
    pub error: Option<String>,

    #[pyo3(get)]
    pub tasks: HashMap<String, Score>,

    #[pyo3(get)]
    pub id: String,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct LLMEvalRecord {
    pub id: String,
    pub context: Value,
}

#[pymethods]
impl LLMEvalRecord {
    #[new]
    #[pyo3(signature = (
        context,
        id=None
    ))]

    /// Creates a new LLMRecord instance.
    /// The context is either a python dictionary or a pydantic basemodel.
    pub fn new(
        py: Python<'_>,
        context: Bound<'_, PyAny>,
        id: Option<String>,
    ) -> Result<Self, EvaluationError> {
        // check if context is a PyDict or PyObject(Pydantic model)
        let context_val = if context.is_instance_of::<PyDict>() {
            pyobject_to_json(&context)?
        } else if is_pydantic_model(py, &context)? {
            // Dump pydantic model to dictionary
            let model = context.call_method0("model_dump")?;

            // Serialize the dictionary to JSON
            pyobject_to_json(&model)?
        } else {
            Err(EvaluationError::MustBeDictOrBaseModel)?
        };

        let id = id.unwrap_or_else(create_uuid7);

        Ok(LLMEvalRecord {
            id,
            context: context_val,
        })
    }

    #[getter]
    pub fn context<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, EvaluationError> {
        Ok(json_to_pyobject_value(py, &self.context)?
            .into_bound_py_any(py)?
            .clone())
    }
}

#[pyclass]
pub struct EvalResultIter {
    inner: std::vec::IntoIter<EvalResult>,
}

#[pymethods]
impl EvalResultIter {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<EvalResult> {
        slf.inner.next()
    }
}

#[pyclass]
pub struct LLMEvalResults {
    pub results: HashMap<String, EvalResult>,
}

#[pymethods]
impl LLMEvalResults {
    pub fn __getitem__(&self, key: &str) -> Result<EvalResult, EvaluationError> {
        match self.results.get(key) {
            Some(value) => Ok(value.clone()),
            None => Err(EvaluationError::MissingKeyError(key.to_string())),
        }
    }

    pub fn __iter__(slf: PyRef<'_, Self>) -> Result<Py<EvalResultIter>, EvaluationError> {
        let iter = EvalResultIter {
            inner: slf
                .results
                .values()
                .cloned()
                .collect::<Vec<_>>()
                .into_iter(),
        };
        Ok(Py::new(slf.py(), iter)?)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl LLMEvalResults {
    fn new() -> Self {
        Self {
            results: HashMap::new(),
        }
    }

    fn add_result(&mut self, data_id: String, result: EvalResult) {
        self.results.insert(data_id, result);
    }
}

/// Process a workflow result and extract scores from completed tasks
fn process_workflow_result(
    workflow_result: Arc<RwLock<Workflow>>,
    data_id: String,
) -> Result<EvalResult, EvaluationError> {
    let mut eval_result = EvalResult {
        error: None,
        tasks: HashMap::new(),
        id: data_id.clone(),
    };

    let workflow = workflow_result
        .read()
        .map_err(|_| WorkflowError::LockAcquireError)?;

    let tasks = workflow.task_list.tasks();
    for task in tasks.values() {
        if let (TaskStatus::Completed, Some(result)) = (&task.status, &task.result) {
            if let Some(content) = result.content() {
                match Score::model_validate_json_str(&content) {
                    Ok(score) => {
                        eval_result.tasks.insert(task.id.clone(), score);
                    }
                    Err(e) => {
                        error!("Failed to validate score for task {}: {:?}", task.id, e);
                        // Continue processing other tasks instead of failing completely
                    }
                }
            }
        }
    }

    Ok(eval_result)
}

fn handle_workflow_result(
    result: Result<Arc<RwLock<Workflow>>, WorkflowError>,
    data_id: String,
) -> EvalResult {
    match result {
        Ok(workflow_result) => match process_workflow_result(workflow_result, data_id.clone()) {
            Ok(eval_result) => eval_result,
            Err(e) => EvalResult {
                error: Some(e.to_string()),
                tasks: HashMap::new(),
                id: data_id,
            },
        },
        Err(e) => EvalResult {
            error: Some(e.to_string()),
            tasks: HashMap::new(),
            id: data_id,
        },
    }
}

async fn spawn_evaluation_tasks(
    workflow: Workflow,
    records: Vec<LLMEvalRecord>,
) -> JoinSet<LLMEvalTaskResult> {
    let mut join_set = JoinSet::new();

    for item in records {
        let inner_workflow = workflow.clone();

        join_set.spawn(async move {
            let result = inner_workflow.run(Some(item.context)).await;
            (result, item.id)
        });
    }

    join_set
}

type LLMEvalTaskResult = (Result<Arc<RwLock<Workflow>>, WorkflowError>, String);

/// Wait for all evaluation tasks to complete and collect results
async fn collect_evaluation_results(
    mut join_set: JoinSet<LLMEvalTaskResult>,
) -> Result<LLMEvalResults, EvaluationError> {
    let mut eval_results = LLMEvalResults::new();

    while let Some(join_result) = join_set.join_next().await {
        let (workflow_result, data_id) = join_result?;
        let eval_result = handle_workflow_result(workflow_result, data_id.clone());
        eval_results.add_result(data_id, eval_result);
    }

    Ok(eval_results)
}

#[instrument(skip_all)]
async fn async_evaluate_llm(
    workflow: Workflow,
    records: Vec<LLMEvalRecord>,
) -> Result<LLMEvalResults, EvaluationError> {
    debug!("Starting LLM evaluation for {} items", records.len());

    let join_set = spawn_evaluation_tasks(workflow, records).await;
    let results = collect_evaluation_results(join_set).await?;

    debug!(
        "Completed LLM evaluation with {} results",
        results.results.len()
    );
    Ok(results)
}

#[pyfunction]
/// Function for evaluating LLM response and generating metrics.
/// The primary use case for evaluate_llm is to take a list of data samples, which often contain inputs and outputs
/// from LLM systems and evaluate them against user-defined metrics in a LLM as a judge pipeline. The user is expected provide
/// a list of dict objects and a list of LLMEval metrics. These eval metrics will be used to create a workflow, which is then
/// executed in an async context. All eval scores are extracted and returned to the user.
/// # Arguments
/// * `py`: The Python interpreter instance.
/// * `data`: A list of data samples to evaluate.
/// * `metrics`: A list of evaluation metrics to use.
pub fn evaluate_llm(
    records: Vec<LLMEvalRecord>,
    metrics: Vec<LLMEvalMetric>,
) -> Result<LLMEvalResults, EvaluationError> {
    let workflow = PyWorkflow::from_eval_metrics(metrics, "LLM Evaluation")?;

    // Use the workflow's runtime to execute the async function
    let results = workflow
        .runtime
        .block_on(async { async_evaluate_llm(workflow.workflow, records).await })?;

    Ok(results)
}
