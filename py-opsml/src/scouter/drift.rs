use pyo3::prelude::*;
use scouter_client::*;

pub fn add_drift_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDrifter>()?;
    m.add_class::<DriftProfile>()?;
    m.add_class::<SpcDriftProfile>()?;
    m.add_class::<SpcFeatureDriftProfile>()?;
    m.add_class::<SpcDriftMap>()?;
    m.add_class::<SpcFeatureDrift>()?;
    m.add_class::<SpcDriftConfig>()?;
    m.add_class::<FeatureMap>()?;
    m.add_class::<PsiDriftConfig>()?;
    m.add_class::<PsiDriftProfile>()?;
    m.add_class::<Bin>()?;
    m.add_class::<PsiFeatureDriftProfile>()?;
    m.add_class::<PsiDriftMap>()?;
    m.add_class::<CustomMetric>()?;
    m.add_class::<CustomMetricDriftConfig>()?;
    m.add_class::<CustomDriftProfile>()?;
    m.add_class::<QuantileBinning>()?;
    m.add_class::<EqualWidthBinning>()?;
    m.add_class::<Manual>()?;
    m.add_class::<SquareRoot>()?;
    m.add_class::<Sturges>()?;
    m.add_class::<Rice>()?;
    m.add_class::<Doane>()?;
    m.add_class::<Scott>()?;
    m.add_class::<TerrellScott>()?;
    m.add_class::<FreedmanDiaconis>()?;

    // GenAI Evals
    m.add_class::<GenAIEvalConfig>()?;
    m.add_class::<GenAIEvalProfile>()?;
    m.add_class::<GenAIEvalRecord>()?;
    m.add_class::<LLMJudgeTask>()?;
    m.add_class::<AssertionTask>()?;
    m.add_class::<ComparisonOperator>()?;

    m.add_class::<TraceAssertion>()?;
    m.add_class::<TraceAssertionTask>()?;
    m.add_class::<AggregationType>()?;
    m.add_class::<SpanFilter>()?;
    m.add_class::<SpanStatus>()?;
    m.add_class::<AssertionResult>()?;
    m.add_class::<AssertionResults>()?;
    m.add_function(wrap_pyfunction!(execute_trace_assertion_tasks, m)?)?;

    Ok(())
}
