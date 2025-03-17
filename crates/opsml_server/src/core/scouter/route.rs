use crate::core::scouter;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::State, http::StatusCode, response::IntoResponse, routing::post, Extension, Json,
    Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_client::RequestType;
use scouter_client::ProfileRequest;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

pub async fn insert_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to exchange token for scouter"})),
        )
    })?;

    let profile = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize profile request: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to serialize profile request"})),
        )
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Profile,
            RequestType::Post,
            Some(profile),
            None,
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to insert drift profile: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to insert drift profile"})),
            )
        })?;

    // return

    // Get status code from Scouter response
    let status = response.status();

    // Get JSON body from Scouter response
    let body = response.json::<serde_json::Value>().await.map_err(|e| {
        error!("Failed to parse scouter response: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to parse scouter response"})),
        )
    })?;

    // Pass through the status code and body from Scouter
    if status.is_success() {
        Ok((status, Json(body)))
    } else {
        Err((status, Json(body)))
    }
}

pub async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{}/scouter/profile", prefix),
            post(insert_drift_profile),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter router");
            // panic
            Err(anyhow::anyhow!("Failed to create scouter router"))
                .context("Panic occurred while creating the router")
        }
    }
}
