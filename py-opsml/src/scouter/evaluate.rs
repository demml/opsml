use pyo3::prelude::*;
use scouter_client::{
    AlignedEvalResult, EvaluationConfig, GenAIEvalDataset, GenAIEvalResultSet, GenAIEvalResults,
    GenAIEvalSet, GenAIEvalTaskResult,
};

pub fn add_evaluate_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GenAIEvalResults>()?;
    m.add_class::<EvaluationConfig>()?;
    m.add_class::<GenAIEvalDataset>()?;

    m.add_class::<GenAIEvalSet>()?;
    m.add_class::<GenAIEvalTaskResult>()?;
    m.add_class::<GenAIEvalResultSet>()?;
    m.add_class::<AlignedEvalResult>()?;

    //m.add_function(wrap_pyfunction!(evaluate_genai, m)?)?;
    Ok(())
}
