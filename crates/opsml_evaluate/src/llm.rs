use crate::error::EvaluationError;
use opsml_state::app_state;
use opsml_types::contracts::evaluation::LLMEvalTaskResultRecord;
use opsml_utils::get_utc_datetime;
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
#[pyo3(signature = (records, metrics, config=None, log=false))]
pub fn evaluate_llm(
    records: Vec<LLMEvalRecord>,
    metrics: Vec<LLMEvalMetric>,
    config: Option<EvaluationConfig>,
    log: bool,
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

    if log {
        // create evaluation record
        // should return the artifact key
        // encrypt (serialize all data)
        // upload
    }

    Ok(results)
}

/// Helper function for creating LLM evaluation records from results
/// # Arguments
/// * `evaluation_uid` - The UID of the evaluation
/// * `evaluation_name` - The name of the evaluation
/// * `results` - The results of the evaluation
/// # Returns
/// * `Vec<LLMEvalTaskResultRecord>` - A vector of LLM evaluation
fn create_llm_evaluation_records(
    evaluation_uid: String,
    evaluation_name: String,
    results: &LLMEvalResults,
) -> Result<Vec<LLMEvalTaskResultRecord>, EvaluationError> {
    let mut records = vec![];
    for (i, task) in results.results.values().enumerate() {
        let metrics = serde_json::to_string(&task.metrics)?;
        let mean_embeddings = serde_json::to_string(&task.mean_embeddings)?;
        let similarity_scores = serde_json::to_string(&task.similarity_scores)?;
        let cluster_id = results
            .array_dataset
            .as_ref()
            .and_then(|arr| arr.clusters.get(i).cloned());
        records.push(LLMEvalTaskResultRecord {
            evaluation_uid: evaluation_uid.clone(),
            id: task.id.clone(),
            evaluation_name: evaluation_name.clone(),
            created_at: get_utc_datetime(),
            metrics,
            mean_embeddings,
            similarity_scores,
            cluster_id,
        });
    }
    Ok(records)
}
