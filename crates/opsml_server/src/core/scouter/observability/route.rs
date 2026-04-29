use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::scouter;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::{Query, State},
    http::StatusCode,
    routing::get,
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_types::api::RequestType;
use opsml_types::contracts::{Operation, ResourceType};
use scouter_client::ScouterServerError;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

#[utoipa::path(
    get,
    path = "/opsml/api/scouter/observability/metrics",
    responses(
        (status = 200, description = "Observability metrics", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_observability_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<serde_json::Value>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string", None)
    })?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::ObservabilityMetrics,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get observability metrics: {e}");
            internal_server_error(e, "Failed to get observability metrics", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: "observability_metrics".to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<serde_json::Value>().await.map_err(|e| {
                error!("Failed to parse scouter response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn get_scouter_observability_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{prefix}/scouter/observability/metrics"),
            get(get_observability_metrics),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter observability router");
            Err(anyhow::anyhow!(
                "Failed to create scouter observability router"
            ))
            .context("Panic occurred while creating the observability router")
        }
    }
}
