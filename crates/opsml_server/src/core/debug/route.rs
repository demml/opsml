use crate::core::debug::schema::{ConnectionInfo, DebugInfo};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::extract::State;
use axum::routing::get;
use axum::Router;
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

#[axum::debug_handler]
async fn debug_connections(State(data): State<Arc<AppState>>) -> ConnectionInfo {
    let cnx_tracker = &data.connection_tracker;

    // if connection tracking is not enabled, return None
    if let Some(tracker) = cnx_tracker {
        ConnectionInfo {
            connections: tracker
                .connections
                .lock()
                .unwrap()
                .keys()
                .cloned()
                .collect(),
            total_connections: tracker.total_connections.clone(),
            peak_connections: tracker.peak_connections.clone(),
            api_connections: tracker.api_connections.clone(),
            spa_connections: tracker.spa_connections.clone(),
            request_counter: tracker.request_counter.clone(),
        }
    } else {
        ConnectionInfo::not_implemented()
    }
}

pub async fn get_debug_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/debug"), get(debug_info))
            .route(
                &format!("{prefix}/debug/connections"),
                get(debug_connections),
            )
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
