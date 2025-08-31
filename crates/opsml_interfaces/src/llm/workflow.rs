use opsml_state::app_state;
use opsml_types::cards::experiment::LLMEvalMetric;
use potato_head::{
    json_to_pydict, parse_response_to_json, pyobject_to_json, PyAgent, Task, TaskList, Workflow,
    WorkflowError, WorkflowResult,
};
use potato_head::{Agent, Provider};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use tracing::{debug, error, info};

#[pyclass(name = "Workflow")]
#[derive(Debug, Clone)]
pub struct PyWorkflow {
    pub workflow: Workflow,

    // allow adding output types for python tasks (py only)
    // these are provided at runtime by the user and must match the response
    // format of the prompt the task is associated with
    output_types: HashMap<String, Arc<PyObject>>,

    // potatohead version holds a reference to the runtime
    pub runtime: Arc<tokio::runtime::Runtime>,
}

#[pymethods]
impl PyWorkflow {
    #[new]
    #[pyo3(signature = (name))]
    pub fn new(name: &str) -> Result<Self, WorkflowError> {
        info!("Creating new workflow: {}", name);
        let runtime = app_state().runtime.clone();
        Ok(Self {
            workflow: Workflow::new(name),
            output_types: HashMap::new(),
            runtime,
        })
    }

    #[getter]
    pub fn name(&self) -> String {
        self.workflow.name.clone()
    }

    #[getter]
    pub fn task_list(&self) -> TaskList {
        self.workflow.task_list.clone()
    }

    #[getter]
    pub fn is_workflow(&self) -> bool {
        true
    }

    #[getter]
    pub fn __workflow__(&self) -> String {
        self.model_dump_json()
    }

    #[getter]
    pub fn agents(&self) -> Result<HashMap<String, PyAgent>, WorkflowError> {
        self.workflow
            .agents
            .iter()
            .map(|(id, agent)| {
                Ok((
                    id.clone(),
                    PyAgent {
                        agent: agent.clone(),
                        runtime: self.runtime.clone(),
                    },
                ))
            })
            .collect::<Result<HashMap<_, _>, _>>()
    }

    #[pyo3(signature = (task_output_types))]
    pub fn add_task_output_types<'py>(
        &mut self,
        task_output_types: Bound<'py, PyDict>,
    ) -> PyResult<()> {
        let converted: HashMap<String, Arc<PyObject>> = task_output_types
            .iter()
            .map(|(k, v)| -> PyResult<(String, Arc<PyObject>)> {
                // Explicitly return a Result from the closure
                let key = k.extract::<String>()?;
                let value = v.clone().unbind();
                Ok((key, Arc::new(value)))
            })
            .collect::<PyResult<_>>()?;
        self.output_types.extend(converted);
        Ok(())
    }

    #[pyo3(signature = (task, output_type = None))]
    pub fn add_task(
        &mut self,
        py: Python<'_>,
        mut task: Task,
        output_type: Option<Bound<'_, PyAny>>,
    ) -> Result<(), WorkflowError> {
        if let Some(output_type) = output_type {
            // Parse and set the response format
            (task.prompt.response_type, task.prompt.response_json_schema) =
                parse_response_to_json(py, &output_type)
                    .map_err(|e| WorkflowError::InvalidOutputType(e.to_string()))?;

            // Store the output type for later use
            self.output_types
                .insert(task.id.clone(), Arc::new(output_type.unbind()));
        }

        self.workflow.task_list.add_task(task)?;
        Ok(())
    }

    pub fn add_tasks(&mut self, tasks: Vec<Task>) -> Result<(), WorkflowError> {
        for task in tasks {
            self.workflow.task_list.add_task(task)?;
        }
        Ok(())
    }

    pub fn add_agent(&mut self, agent: &Bound<'_, PyAgent>) {
        // extract the arc rust agent from the python agent
        let agent = agent.extract::<PyAgent>().unwrap().agent.clone();
        self.workflow.agents.insert(agent.id.clone(), agent);
    }

    pub fn is_complete(&self) -> bool {
        self.workflow.task_list.is_complete()
    }

    pub fn pending_count(&self) -> usize {
        self.workflow.task_list.pending_count()
    }

    pub fn execution_plan<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, PyDict>, WorkflowError> {
        let plan = self.workflow.execution_plan()?;
        debug!("Execution plan: {:?}", plan);

        // turn hashmap into a to json
        let json = serde_json::to_value(plan).map_err(|e| {
            error!("Failed to serialize execution plan to JSON: {}", e);
            e
        })?;

        let pydict = PyDict::new(py);
        json_to_pydict(py, &json, &pydict)?;

        Ok(pydict)
    }

    #[pyo3(signature = (global_context=None))]
    pub fn run(
        &self,
        py: Python,
        global_context: Option<Bound<'_, PyDict>>,
    ) -> Result<WorkflowResult, WorkflowError> {
        info!("Running workflow: {}", self.workflow.name);

        // Convert the global context from PyDict to serde_json::Value if provided
        let global_context = if let Some(context) = global_context {
            // Convert PyDict to serde_json::Value
            let json_value = pyobject_to_json(&context.into_bound_py_any(py)?)?;
            Some(json_value)
        } else {
            None
        };

        let workflow: Arc<RwLock<Workflow>> = self
            .runtime
            .block_on(async { self.workflow.run(global_context).await })?;

        // Try to get exclusive ownership of the workflow by unwrapping the Arc if there's only one reference
        let workflow_result = match Arc::try_unwrap(workflow) {
            // If we have exclusive ownership, we can consume the RwLock
            Ok(rwlock) => {
                // Unwrap the RwLock to get the Workflow
                let workflow = rwlock
                    .into_inner()
                    .map_err(|_| WorkflowError::LockAcquireError)?;

                // Get the events before creating WorkflowResult
                let events = workflow
                    .event_tracker
                    .read()
                    .unwrap()
                    .events
                    .read()
                    .unwrap()
                    .clone();

                // Move the tasks out of the workflow
                WorkflowResult::new(py, workflow.task_list.tasks(), &self.output_types, events)
            }
            // If there are other references, we need to clone
            Err(arc) => {
                // Just read the workflow
                error!("Workflow still has other references, reading instead of consuming.");
                let workflow = arc
                    .read()
                    .map_err(|_| WorkflowError::ReadLockAcquireError)?;

                // Get the events before creating WorkflowResult
                let events = workflow
                    .event_tracker
                    .read()
                    .unwrap()
                    .events
                    .read()
                    .unwrap()
                    .clone();

                WorkflowResult::new(py, workflow.task_list.tasks(), &self.output_types, events)
            }
        };

        info!("Workflow execution completed successfully.");
        Ok(workflow_result)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(&self.workflow).unwrap()
    }

    #[staticmethod]
    #[pyo3(signature = (json_string, output_types=None))]
    pub fn model_validate_json(
        json_string: String,
        output_types: Option<Bound<'_, PyDict>>,
    ) -> Result<Self, WorkflowError> {
        let workflow: Workflow = serde_json::from_str(&json_string)?;
        let runtime = Arc::new(
            tokio::runtime::Runtime::new()
                .map_err(|e| WorkflowError::RuntimeError(e.to_string()))?,
        );

        let output_types = if let Some(output_types) = output_types {
            output_types
                .iter()
                .map(|(k, v)| -> PyResult<(String, Arc<PyObject>)> {
                    let key = k.extract::<String>()?;
                    let value = v.clone().unbind();
                    Ok((key, Arc::new(value)))
                })
                .collect::<PyResult<HashMap<String, Arc<PyObject>>>>()?
        } else {
            HashMap::new()
        };

        let py_workflow = PyWorkflow {
            workflow,
            output_types,
            runtime,
        };

        Ok(py_workflow)
    }
}

impl PyWorkflow {
    /// Create a pyworkflow from evaluation metrics
    /// # Arguments
    /// * `eval_metrics`: A vector of evaluation metrics to create the workflow from.
    /// * `name`: The name of the workflow.
    pub fn from_eval_metrics(
        eval_metrics: Vec<LLMEvalMetric>,
        name: &str,
    ) -> Result<Self, WorkflowError> {
        // Build a workflow from metrics
        let mut workflow = Workflow::new(name);
        let mut agents: HashMap<Provider, Agent> = HashMap::new();
        let mut metric_names = Vec::new();

        // Create agents. We don't want to duplicate, so we check if the agent already exists.
        // if it doesn't, we create it.
        for metric in &eval_metrics {
            let provider = Provider::from_string(&metric.prompt.model_settings.provider)
                .map_err(|e| WorkflowError::Error(format!("Failed to parse provider: {}", e)))?;

            let agent = match agents.entry(provider) {
                Entry::Occupied(entry) => entry.into_mut(),
                Entry::Vacant(entry) => {
                    let agent =
                        Agent::from_model_settings(&metric.prompt.model_settings).map_err(|e| {
                            WorkflowError::Error(format!("Failed to create agent: {}", e))
                        })?;
                    workflow.add_agent(&agent);
                    entry.insert(agent)
                }
            };

            let task = Task::new(&agent.id, metric.prompt.clone(), &metric.name, None, None);
            workflow.add_task(task)?;
            metric_names.push(metric.name.clone());
        }

        let runtime = app_state().runtime.clone();
        Ok(Self {
            workflow,
            output_types: HashMap::new(),
            runtime,
        })
    }
}
