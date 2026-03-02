use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::Json;
/// Route for debugging information
use axum::extract::State;
use axum::{Router, routing::get};
use opsml_types::contracts::{StorageSettings, UiSettings};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::error;

pub async fn storage_settings(State(data): State<Arc<AppState>>) -> Json<StorageSettings> {
    Json(StorageSettings {
        storage_type: data.storage_client.storage_type(),
    })
}

pub async fn ui_settings(State(data): State<Arc<AppState>>) -> Json<UiSettings> {
    Json(UiSettings {
        scouter_enabled: data.scouter_client.is_enabled(),
        sso_enabled: data.auth_manager.sso_provider.is_some(),
    })
}

pub async fn get_settings_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/storage/settings"), get(storage_settings))
            .route(&format!("{prefix}/ui/settings"), get(ui_settings))
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
