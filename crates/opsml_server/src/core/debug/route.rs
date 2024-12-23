use crate::core::debug::schema::DebugInfo;
use crate::core::state::AppState;
use anyhow::{Context, Result};
/// Route for debugging information
use axum::extract::State;
use axum::{routing::get, Router};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

pub async fn debug_info(State(data): State<Arc<AppState>>) -> DebugInfo {
    DebugInfo::new(
        data.storage_client.name().to_string(),
        data.config.opsml_storage_uri.to_owned(),
        data.config.opsml_tracking_uri.to_owned(),
    )
}

pub async fn get_debug_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(&format!("{}/debug", prefix), get(debug_info))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create debug router");
            // panic
            Err(anyhow::anyhow!("Failed to create debug router"))
                .context("Panic occurred while creating the router")
        }
    }
}
