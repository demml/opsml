use pyo3::prelude::*;
use scouter_client::{
    AlignedEvalResult, ComparisonResults, EvaluationConfig, GenAIEvalDataset, GenAIEvalResultSet,
    GenAIEvalResults, GenAIEvalSet, GenAIEvalTaskResult, MissingTask, TaskComparison,
    WorkflowComparison,
};

pub fn add_evaluate_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GenAIEvalResults>()?;
    m.add_class::<EvaluationConfig>()?;
    m.add_class::<GenAIEvalDataset>()?;

    m.add_class::<GenAIEvalSet>()?;
    m.add_class::<GenAIEvalTaskResult>()?;
    m.add_class::<GenAIEvalResultSet>()?;
    m.add_class::<AlignedEvalResult>()?;

    m.add_class::<MissingTask>()?;
    m.add_class::<ComparisonResults>()?;
    m.add_class::<TaskComparison>()?;
    m.add_class::<WorkflowComparison>()?;

    Ok(())
}
