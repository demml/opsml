use core::fmt::Debug;
use opsml_interfaces::llm::workflow::PyWorkflow;
use opsml_types::cards::LLMEvalMetric;
use opsml_utils::PyHelperFuncs;
use potato_head::prompt::ResponseType;
use potato_head::Prompt;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};

use crate::error::EvaluationError;

pub fn evaluate_llm(
    py: Python,
    data: Option<Bound<'_, PyDict>>,
    metrics: Vec<LLMEvalMetric>,
) -> Result<(), EvaluationError> {
    let workflow = PyWorkflow::from_eval_metrics(metrics, "LLM Evaluation")?;
    Ok(())
}
