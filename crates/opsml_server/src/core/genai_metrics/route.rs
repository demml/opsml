use crate::core::scouter::genai::{
    get_service_genai_timeseries, get_span_genai_metrics, get_trace_genai_aggregate,
};
use crate::core::state::AppState;
use anyhow::Result;
use axum::{Router, routing::get};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::error;

pub async fn get_genai_metrics_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/traces/{{trace_id}}/aggregate"), get(get_trace_genai_aggregate))
            .route(&format!("{prefix}/spans/{{span_id}}/metrics"), get(get_span_genai_metrics))
            .route(&format!("{prefix}/services/{{service_id}}/timeseries"), get(get_service_genai_timeseries))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create genai_metrics router");
            Err(anyhow::anyhow!("Failed to create genai_metrics router"))
        }
    }
}
