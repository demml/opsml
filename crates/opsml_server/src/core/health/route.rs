use crate::core::health::schema::Alive;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{routing::get, Router};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;

pub async fn health_check() -> Alive {
    Alive::default()
}

pub async fn get_health_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(&format!("{}/healthcheck", prefix), get(health_check))
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
