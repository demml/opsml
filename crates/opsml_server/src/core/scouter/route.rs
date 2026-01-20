use crate::core::scouter::{
    alerts::get_scouter_alert_router, drift::get_scouter_drift_router,
    genai::get_scouter_genai_router, health::get_scouter_health_router,
    profile::get_scouter_profile_router, tags::get_scouter_tags_router,
    trace::get_scouter_trace_router,
};
use crate::core::state::AppState;
use anyhow::Result;
use axum::Router;
use std::sync::Arc;

pub(crate) async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let alert_routes = get_scouter_alert_router(prefix).await?;

    let merged = Router::new()
        .merge(alert_routes)
        .merge(get_scouter_drift_router(prefix).await?)
        .merge(get_scouter_genai_router(prefix).await?)
        .merge(get_scouter_health_router(prefix).await?)
        .merge(get_scouter_profile_router(prefix).await?)
        .merge(get_scouter_tags_router(prefix).await?)
        .merge(get_scouter_trace_router(prefix).await?);

    Ok(merged)
}
