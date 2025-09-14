pub use opsml_evaluate::llm::evaluate_llm;
use pyo3::prelude::*;
pub use scouter_client::{
    EvaluationConfig, LLMEvalMetric, LLMEvalRecord, LLMEvalResults, LLMEvalTaskResult,
};

#[pymodule]
pub fn evaluate(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LLMEvalTaskResult>()?;
    m.add_class::<LLMEvalMetric>()?;
    m.add_class::<LLMEvalRecord>()?;
    m.add_class::<LLMEvalResults>()?;
    m.add_class::<EvaluationConfig>()?;
    m.add_function(wrap_pyfunction!(evaluate_llm, m)?)?;
    Ok(())
}
