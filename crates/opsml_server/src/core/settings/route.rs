use crate::core::state::AppState;
use anyhow::{Context, Result};
/// Route for debugging information
use axum::extract::State;
use axum::Json;
use axum::{routing::get, Router};
use opsml_contracts::StorageSettings;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

pub async fn storage_settings(State(data): State<Arc<AppState>>) -> Json<StorageSettings> {
    Json(StorageSettings {
        storage_type: data.storage_client.storage_type(),
    })
}

pub async fn get_settings_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{}/storage/settings", prefix),
            get(storage_settings),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create settings router");
            // panic
            Err(anyhow::anyhow!("Failed to create settings router"))
                .context("Panic occurred while creating the router")
        }
    }
}
