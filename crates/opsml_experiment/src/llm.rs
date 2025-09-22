use opsml_evaluate::llm::evaluate_llm;
use pyo3::prelude::*;
use scouter_client::{EvaluationConfig, LLMEvalMetric, LLMEvalRecord, LLMEvalResults};

use crate::error::ExperimentError;

#[pyclass]
pub struct LLMEvaluator {}

#[pymethods]
impl LLMEvaluator {
    /// Helper function to expose evaluat_llm function from the Experiment struct
    #[staticmethod]
    pub fn evaluate(
        records: Vec<LLMEvalRecord>,
        metrics: Vec<LLMEvalMetric>,
        config: Option<EvaluationConfig>,
    ) -> Result<LLMEvalResults, ExperimentError> {
        Ok(evaluate_llm(records, metrics, config, false)?)
    }
}
