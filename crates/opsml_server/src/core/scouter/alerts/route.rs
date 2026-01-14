use crate::core::error::{internal_server_error, OpsmlServerError};

use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{extract::State, http::StatusCode, routing::post, Extension, Json, Router};
use opsml_auth::permission::UserPermissions;

use opsml_types::api::RequestType;

use scouter_client::{
    DriftAlertPaginationRequest, DriftAlertPaginationResponse, ScouterServerError,
    UpdateAlertResponse, UpdateAlertStatus,
};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;

use tracing::error;

/// Get drift alerts
pub async fn drift_alerts(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<DriftAlertPaginationRequest>,
) -> Result<Json<DriftAlertPaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Alerts,
            RequestType::Post,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize alert request: {e}");
                internal_server_error(e, "Failed to serialize alert request")
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift alerts: {e}");
            internal_server_error(e, "Failed to get drift alerts")
        })?;

    let status_code = response.status();

    match status_code.is_success() {
        true => {
            let body = response
                .json::<DriftAlertPaginationResponse>()
                .await
                .map_err(|e| {
                    error!("Failed to parse scouter response: {e}");
                    internal_server_error(e, "Failed to parse scouter response")
                })?;

            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Acknowledge drift alerts
pub async fn update_alert_status(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<UpdateAlertStatus>,
) -> Result<Json<UpdateAlertResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_write_permission(&body.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Alerts,
            RequestType::Put,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize alert request: {e}");
                internal_server_error(e, "Failed to serialize alert request")
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to acknowledge drift alerts: {e}");
            internal_server_error(e, "Failed to acknowledge drift alerts")
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<UpdateAlertResponse>().await.map_err(|e| {
                error!("Failed to parse scouter response: {e}");
                internal_server_error(e, "Failed to parse scouter response")
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn get_scouter_alert_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{prefix}/scouter/alerts"),
            post(drift_alerts).put(update_alert_status),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter alert router");
            Err(anyhow::anyhow!("Failed to create scouter alert router"))
                .context("Panic occurred while creating the router")
        }
    }
}
