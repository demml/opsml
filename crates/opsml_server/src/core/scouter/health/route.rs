use crate::core::scouter;

use crate::core::error::OpsmlServerError;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{Extension, Json, Router, extract::State, http::StatusCode, routing::get};
use opsml_auth::permission::UserPermissions;

use opsml_types::Alive;
use opsml_types::api::RequestType;

use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument, warn};

#[instrument(skip_all)]
pub async fn check_scouter_health(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
) -> Result<Json<Alive>, (StatusCode, Json<OpsmlServerError>)> {
    // Scouter is either not configured or the background watcher has marked it as down.
    // Return alive:false with 200 so the UI can degrade gracefully rather than error.
    if !state.scouter_client.is_enabled() {
        return Ok(Json(Alive { alive: false }));
    }

    let exchange_token = match state.exchange_token_from_perms(&perms).await {
        Ok(token) => token,
        Err(e) => {
            warn!("Failed to exchange token for scouter healthcheck (non-fatal): {e}");
            return Ok(Json(Alive { alive: false }));
        }
    };

    let response = match state
        .scouter_client
        .request(
            scouter::Routes::Healthcheck,
            RequestType::Get,
            None,
            None,
            None,
            &exchange_token,
        )
        .await
    {
        Ok(r) => r,
        Err(e) => {
            // Connection refused or timeout — Scouter is offline. Degrade gracefully.
            warn!("Scouter healthcheck request failed (Scouter may be offline): {e}");
            return Ok(Json(Alive { alive: false }));
        }
    };

    if response.status().is_success() {
        Ok(Json(Alive { alive: true }))
    } else {
        error!(
            "Scouter healthcheck returned non-success status: {}",
            response.status()
        );
        Ok(Json(Alive { alive: false }))
    }
}

pub async fn get_scouter_health_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{prefix}/scouter/healthcheck"),
            get(check_scouter_health),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter health router");
            Err(anyhow::anyhow!("Failed to create scouter health router"))
                .context("Panic occurred while creating the router")
        }
    }
}
