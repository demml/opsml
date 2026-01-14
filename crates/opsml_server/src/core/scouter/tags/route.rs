use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{extract::State, http::StatusCode, routing::post, Extension, Json, Router};
use opsml_auth::permission::UserPermissions;

use opsml_types::api::RequestType;

use scouter_client::{EntityIdTagsRequest, EntityIdTagsResponse, ScouterServerError};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, instrument};

/// Get entity from tags
#[instrument(skip_all)]
pub async fn entity_from_tags(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<EntityIdTagsRequest>,
) -> Result<Json<EntityIdTagsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::TagEntity,
            RequestType::Post,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize request body: {e}");
                internal_server_error(e, "Failed to serialize request body")
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get entity from tags: {e}");
            internal_server_error(e, "Failed to get entity from tags")
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<EntityIdTagsResponse>().await.map_err(|e| {
                error!("Failed to parse scouter tag entity response: {e}");
                internal_server_error(e, "Failed to parse scouter tag entity response")
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

pub async fn get_scouter_tags_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{prefix}/scouter/tags/entity"),
            post(entity_from_tags),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter tags router");
            Err(anyhow::anyhow!("Failed to create scouter tags router"))
                .context("Panic occurred while creating the tags router")
        }
    }
}
