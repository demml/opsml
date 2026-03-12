use pyo3::prelude::*;
use scouter_client::{
    AlignedEvalResult, ComparisonResults, EvalDataset, EvalResultSet, EvalResults, EvalSet,
    EvalTaskResult, EvaluationConfig, EvaluationTaskType, MissingTask, TaskComparison,
    WorkflowComparison,
};

pub fn add_evaluate_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<EvalResults>()?;
    m.add_class::<EvaluationConfig>()?;
    m.add_class::<EvalDataset>()?;

    m.add_class::<EvalSet>()?;
    m.add_class::<EvalTaskResult>()?;
    m.add_class::<EvalResultSet>()?;
    m.add_class::<AlignedEvalResult>()?;

    m.add_class::<MissingTask>()?;
    m.add_class::<ComparisonResults>()?;
    m.add_class::<TaskComparison>()?;
    m.add_class::<WorkflowComparison>()?;
    m.add_class::<EvaluationTaskType>()?;

    Ok(())
}
