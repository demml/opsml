use pyo3::prelude::*;
use scouter_client::{
    AlignedEvalResult, ComparisonResults, EvalDataset, EvalMetrics, EvalResultSet, EvalResults,
    EvalRunner, EvalScenario, EvalScenarios, EvalSet, EvalTaskResult, EvaluationConfig,
    EvaluationTaskType, MissingTask, ScenarioComparisonResults, ScenarioDelta, ScenarioEvalResults,
    ScenarioResult, TaskComparison, TaskSummary, WorkflowComparison,
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
    m.add_class::<EvalScenario>()?;

    m.add_class::<EvalMetrics>()?;
    m.add_class::<ScenarioResult>()?;
    m.add_class::<ScenarioDelta>()?;
    m.add_class::<ScenarioEvalResults>()?;
    m.add_class::<ScenarioComparisonResults>()?;

    m.add_class::<EvalScenarios>()?;
    m.add_class::<EvalRunner>()?;
    m.add_class::<TaskSummary>()?;

    Ok(())
}
