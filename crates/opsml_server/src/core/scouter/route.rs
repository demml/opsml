use crate::core::scouter;
use crate::core::scouter::types::UpdateProfileRequest;
use crate::core::scouter::utils::{find_drift_profile, save_encrypted_profile};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::State, http::StatusCode, response::IntoResponse, routing::post, Extension, Json,
    Router,
};

use opsml_auth::permission::UserPermissions;
use opsml_client::RequestType;
use opsml_sql::base::SqlClient;
use opsml_types::RegistryType;
use opsml_types::SaveName;
use reqwest::Response;
use scouter_client::ProfileRequest;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

async fn return_response(
    response: Response,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
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
    return_response(response).await
}

/// Update a drift profile. Two tasks are performed:
/// 1. Dump updated profile to storage to ensure profiles are syncd (opsml)
/// 2. Send the profile to scouter (scouter)
pub async fn update_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<UpdateProfileRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    if !perms.has_write_permission(&req.repository) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({"error": "User does not have write permission"})),
        ));
    }

    // 1. Opsml task
    let drift_type = req.request.drift_type.to_string();
    let artifact_key = state
        .sql_client
        .get_artifact_key(&req.uid, &RegistryType::Model.to_string())
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to get artifact key"})),
            )
        })?;

    let drift_path = artifact_key.storage_path().join(SaveName::Drift);

    // list files in the directory
    let files = state.storage_client.find(&drift_path).await.map_err(|e| {
        error!("Failed to list files in directory: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to list files in directory"})),
        )
    })?;

    // assert files is not empty
    if files.is_empty() {
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "No files found in directory"})),
        ));
    }

    let filename = find_drift_profile(&files, &drift_type)?;
    let encryption_key = artifact_key.get_decrypt_key().map_err(|e| {
        error!("Failed to get encryption key: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to get encryption key"})),
        )
    })?;

    save_encrypted_profile(
        &req.request.profile,
        &filename,
        &encryption_key,
        &state.storage_client,
        &drift_path,
    )
    .await?;

    // 2. Scouter task
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to exchange token for scouter"})),
        )
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Profile,
            RequestType::Put,
            Some(serde_json::to_value(&req.request).map_err(|e| {
                error!("Failed to serialize profile request: {}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({"error": "Failed to serialize profile request"})),
                )
            })?),
            None,
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to update drift profile"})),
            )
        })?;

    return_response(response).await
}

pub async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{}/scouter/profile", prefix),
            post(insert_drift_profile).put(update_drift_profile),
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
