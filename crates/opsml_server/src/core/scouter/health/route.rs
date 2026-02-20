use crate::core::error::{OpsmlServerError, internal_server_error};

use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{Extension, Json, Router, extract::State, http::StatusCode, routing::get};
use opsml_auth::permission::UserPermissions;

use opsml_types::Alive;
use opsml_types::api::RequestType;

use scouter_client::ScouterServerError;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn check_scouter_health(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
) -> Result<Json<Alive>, (StatusCode, Json<OpsmlServerError>)> {
    // exit early if scouter is not enabled
    if !state.scouter_client.enabled {
        return Ok(Json(Alive { alive: false }));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let response = state
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
        .map_err(|e| {
            error!("Failed to get scouter healthcheck: {e}");
            internal_server_error(e, "Failed to get scouter healthcheck", None)
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let _ = response.json::<Alive>().await.map_err(|e| {
                error!("Failed to parse scouter response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(Alive { alive: true }))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            // return error response
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
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
