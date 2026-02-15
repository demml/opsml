use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::Json;
use axum::response::IntoResponse;
use axum::{Router, routing::get};
use opsml_types::Alive;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;

pub async fn health_check() -> impl IntoResponse {
    Json(Alive::default())
}

pub async fn get_health_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(&format!("{prefix}/healthcheck"), get(health_check))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            // panic
            Err(anyhow::anyhow!("Failed to create health router"))
                .context("Panic occurred while creating the router")
        }
    }
}
