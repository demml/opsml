use opsml_evaluate::llm::evaluate_llm;
use opsml_evaluate::llm::{LLMEvalRecord, LLMEvalResults};
use opsml_types::cards::LLMEvalMetric;
use pyo3::prelude::*;

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
    ) -> Result<LLMEvalResults, ExperimentError> {
        Ok(evaluate_llm(records, metrics)?)
    }
}
