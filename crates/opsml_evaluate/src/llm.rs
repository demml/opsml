use crate::error::EvaluationError;
use core::fmt::Debug;
use opsml_interfaces::llm::workflow::PyWorkflow;
use opsml_types::cards::LLMEvalMetric;
use opsml_utils::pyobject_to_json;
use opsml_utils::PyHelperFuncs;
use potato_head::prompt::ResponseType;
use potato_head::Prompt;
use potato_head::Workflow;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use tokio::task::JoinSet;
use potato_head::WorkflowError;

async fn async_evalulate_llm(
    workflow: Workflow,
    data: Vec<serde_json::Value>,
) -> Result<(), EvaluationError> {
    let mut set = JoinSet::new();
    let result = Vec::new();

    for item in data {
        let inner_workflow = workflow.clone();
        set.spawn(async move {
            inner_workflow.run(Some(item)).await
        });
      
    }

    // Wait for all tasks to complete. may need to call block_on here
    while let Some(res) = set.join_next().await {
        let flow = res??;
        let workflow = flow
                    .into_inner()
                    .map_err(|_| WorkflowError::LockAcquireError)?;
    }
    Ok(())
}

pub fn evaluate_llm(
    py: Python,
    data: Bound<'_, PyList>,
    metrics: Vec<LLMEvalMetric>,
) -> Result<(), EvaluationError> {
    let workflow = PyWorkflow::from_eval_metrics(metrics, "LLM Evaluation")?;

    let runtime = workflow.runtime.clone();
    let mut handles = Vec::new();

    for item in data.iter() {
        //
        let inner_workflow = workflow.workflow.clone();
        let dict = item.downcast::<PyDict>()?;
        let json_value = pyobject_to_json(&dict.into_bound_py_any(py)?)?;
        let handle = runtime.spawn(async move {
            // Process the json_value with the LLM
            inner_workflow.run(Some(json_value)).await
        });

        handles.push(handle);
    }

    // Wait for all tasks to complete. may need to call block_on here
    let _ = futures::future::join_all(handles).await

    Ok(())
}
