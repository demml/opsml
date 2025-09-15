use crate::error::EvaluationError;
use opsml_state::app_state;
use pyo3::prelude::*;
use scouter_client::{
    async_evaluate_llm, workflow_from_eval_metrics, EvaluationConfig, LLMEvalMetric, LLMEvalRecord,
    LLMEvalResults,
};
use std::sync::Arc;

#[pyfunction]
/// Function for evaluating LLM response and generating metrics.
/// The primary use case for evaluate_llm is to take a list of data samples, which often contain inputs and outputs
/// from LLM systems and evaluate them against user-defined metrics in a LLM as a judge pipeline. The user is expected provide
/// a list of dict objects and a list of LLMEval metrics. These eval metrics will be used to create a workflow, which is then
/// executed in an async context. All eval scores are extracted and returned to the user.
/// # Arguments
/// * `py`: The Python interpreter instance.
/// * `data`: A list of data samples to evaluate.
/// * `metrics`: A list of evaluation metrics to use.
/// * `config`: Optional evaluation configuration settings.
#[pyo3(signature = (records, metrics, config=None))]
pub fn evaluate_llm(
    records: Vec<LLMEvalRecord>,
    metrics: Vec<LLMEvalMetric>,
    config: Option<EvaluationConfig>,
) -> Result<LLMEvalResults, EvaluationError> {
    let runtime = app_state().start_runtime();
    let config = Arc::new(config.unwrap_or_default());

    // Create runtime and execute evaluation pipeline
    let mut results = runtime.block_on(async {
        let workflow = workflow_from_eval_metrics(metrics, "LLM Evaluation").await?;
        async_evaluate_llm(workflow, records, &config).await
    })?;

    // Only run post-processing if needed
    // Post processing includes calculating embedding means, similarities, clustering, and histograms
    if config.needs_post_processing() {
        results.finalize(&config)?;
    }

    Ok(results)
}
