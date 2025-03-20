use crate::core::error::internal_server_error;
use crate::core::scouter;
use crate::core::scouter::utils::{find_drift_profile, save_encrypted_profile};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post, put},
    Extension, Json, Router,
};
use scouter_client::{
    BinnedCustomMetrics, BinnedPsiFeatureMetrics, DriftRequest, SpcDriftFeatures,
};

use opsml_auth::permission::UserPermissions;
use opsml_client::RequestType;
use opsml_sql::base::SqlClient;
use opsml_types::contracts::UpdateProfileRequest;
use opsml_types::RegistryType;
use opsml_types::SaveName;
use reqwest::Response;
use scouter_client::ProfileRequest;
use scouter_client::ProfileStatusRequest;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{debug, error, instrument};

async fn return_response(
    response: Response,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    // Get status code from Scouter response
    let status = response.status();

    // Get JSON body from Scouter response
    let body = response.json::<serde_json::Value>().await.map_err(|e| {
        error!("Failed to parse scouter response: {}", e);
        internal_server_error(e, "Failed to parse scouter response")
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
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let profile = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize profile request: {}", e);
        internal_server_error(e, "Failed to serialize profile request")
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
            internal_server_error(e, "Failed to insert drift profile")
        })?;

    // Get status code from Scouter response
    return_response(response).await
}

/// Update a drift profile. Two tasks are performed:
/// 1. Dump updated profile to storage to ensure profiles are syncd (opsml)
/// 2. Send the profile to scouter (scouter)
#[instrument(skip_all)]
pub async fn update_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<UpdateProfileRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    if !perms.has_write_permission(&req.request.repository) {
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
            internal_server_error(e, "Failed to get artifact key")
        })?;

    let drift_path = artifact_key.storage_path().join(SaveName::Drift);

    // list files in the directory
    let files = state.storage_client.find(&drift_path).await.map_err(|e| {
        error!("Failed to list files in directory: {}", e);
        internal_server_error(e, "Failed to list files in directory")
    })?;

    // assert files is not empty
    if files.is_empty() {
        error!("No files found in directory");
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "No files found in directory"})),
        ));
    }

    let filename = find_drift_profile(&files, drift_type)?;
    let encryption_key = artifact_key.get_decrypt_key().map_err(|e| {
        error!("Failed to get encryption key: {}", e);
        return internal_server_error(e, "Failed to get encryption key");
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
        return internal_server_error(e, "Failed to exchange token for scouter");
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Profile,
            RequestType::Put,
            Some(serde_json::to_value(&req.request).map_err(|e| {
                error!("Failed to serialize profile request: {}", e);
                internal_server_error(e, "Failed to serialize profile request")
            })?),
            None,
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile: {}", e);
            internal_server_error(e, "Failed to update drift profile")
        })?;

    return_response(response).await
}

/// Update drift profile status
///
/// # Arguments
///
/// * `data` - Arc<AppState> - Application state
/// * `body` - Json<ProfileStatusRequest> - Profile status request
///
/// # Returns
///
/// * `Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)>` - Result of the request
#[instrument(skip(data, body))]
pub async fn update_drift_profile_status(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileStatusRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    if !perms.has_write_permission(&body.repository) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({ "error": "Permission denied" })),
        ));
    }
    debug!("Updating drift profile status: {:?}", &body);

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::ProfileStatus,
            RequestType::Put,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize profile status request: {}", e);
                internal_server_error(e, "Failed to serialize profile status request")
            })?),
            None,
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile status: {}", e);
            internal_server_error(e, "Failed to update drift profile status")
        })?;

    return_response(response).await
}

#[instrument(skip(data, params))]
pub async fn get_spc_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<SpcDriftFeatures>, (StatusCode, Json<serde_json::Value>)> {
    // validate time window

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {}", e);
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::DriftSpc,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift features: {}", e);
            internal_server_error(e, "Failed to get drift features")
        })?;

    let body = response.json::<SpcDriftFeatures>().await.map_err(|e| {
        error!("Failed to parse drift features: {}", e);
        internal_server_error(e, "Failed to parse drift features")
    })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_psi_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedPsiFeatureMetrics>, (StatusCode, Json<serde_json::Value>)> {
    // validate time window

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {}", e);
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::DriftPsi,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift features: {}", e);
            internal_server_error(e, "Failed to get drift features")
        })?;

    // extract body into SpcDriftFeatures

    let body = response
        .json::<BinnedPsiFeatureMetrics>()
        .await
        .map_err(|e| {
            error!("Failed to parse drift features: {}", e);
            internal_server_error(e, "Failed to parse drift features")
        })?;

    Ok(Json(body))
}

#[instrument(skip(data, params))]
pub async fn get_custom_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedCustomMetrics>, (StatusCode, Json<serde_json::Value>)> {
    // validate time window

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {}", e);
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::DriftCustom,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift features: {}", e);
            internal_server_error(e, "Failed to get drift features")
        })?;

    // extract body into SpcDriftFeatures

    let body = response.json::<BinnedCustomMetrics>().await.map_err(|e| {
        error!("Failed to parse drift features: {}", e);
        internal_server_error(e, "Failed to parse drift features")
    })?;

    Ok(Json(body))
}
pub async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/scouter/profile", prefix),
                post(insert_drift_profile).put(update_drift_profile),
            )
            .route(
                &format!("{}/scouter/profile/status", prefix),
                put(update_drift_profile_status),
            )
            .route(&format!("{}/scouter/drift/spc", prefix), get(get_spc_drift))
            .route(&format!("{}/scouter/drift/psi", prefix), get(get_psi_drift))
            .route(
                &format!("{}/scouter/drift/custom", prefix),
                get(get_custom_drift),
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
