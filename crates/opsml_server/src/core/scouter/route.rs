use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::files::utils::download_artifacts;
use crate::core::scouter;
use crate::core::scouter::types::Alive;
use crate::core::scouter::utils::{find_drift_profile, save_encrypted_profile};
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post, put},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_sql::base::SqlClient;
use opsml_types::api::RequestType;
use opsml_types::contracts::{RawFileRequest, UpdateProfileRequest};
use opsml_types::RegistryType;
use opsml_types::SaveName;
use reqwest::Response;

use crate::core::scouter::types::DriftProfileResult;
use scouter_client::{
    Alerts, BinnedCustomMetrics, BinnedPsiFeatureMetrics, DriftAlertRequest, DriftRequest,
    ProfileRequest, ProfileStatusRequest, ScouterResponse, ScouterServerError, SpcDriftFeatures,
};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::PathBuf;
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{debug, error, instrument};

use crate::core::scouter::utils::load_drift_profiles;

async fn parse_scouter_response(
    response: Response,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let status_code = response.status();

    match status_code.is_success() {
        true => {
            let body = response.json::<ScouterResponse>().await.map_err(|e| {
                error!("Failed to parse scouter response: {}", e);
                internal_server_error(e, "Failed to parse scouter response")
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {}", e);
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn insert_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileRequest>,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
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
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to insert drift profile: {}", e);
            internal_server_error(e, "Failed to insert drift profile")
        })?;

    parse_scouter_response(response).await
}

/// Update a drift profile. Two tasks are performed:
/// 1. Dump updated profile to storage to ensure profiles are syncd (opsml)
/// 2. Send the profile to scouter (scouter)
#[instrument(skip_all)]
pub async fn update_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<UpdateProfileRequest>,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_write_permission(&req.request.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
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
        return OpsmlServerError::no_files_found().into_response(StatusCode::NOT_FOUND);
    }

    let filename = find_drift_profile(&files, drift_type)?;
    let encryption_key = artifact_key.get_decrypt_key().map_err(|e| {
        error!("Failed to get encryption key: {}", e);
        internal_server_error(e, "Failed to get encryption key")
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
        internal_server_error(e, "Failed to exchange token for scouter")
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
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile: {}", e);
            internal_server_error(e, "Failed to update drift profile")
        })?;

    parse_scouter_response(response).await
}

/// Update drift profile status
///
/// # Arguments
/// * `data` - Arc<AppState> - Application state
/// * `body` - Json<ProfileStatusRequest> - Profile status request
///
/// # Returns
/// * `Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)>` - Result of the request
#[instrument(skip(data, body))]
pub async fn update_drift_profile_status(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileStatusRequest>,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_write_permission(&body.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
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
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile status: {}", e);
            internal_server_error(e, "Failed to update drift profile status")
        })?;

    parse_scouter_response(response).await
}

#[instrument(skip(data, params))]
pub async fn get_spc_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<SpcDriftFeatures>, (StatusCode, Json<OpsmlServerError>)> {
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
            &exchange_token,
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
) -> Result<Json<BinnedPsiFeatureMetrics>, (StatusCode, Json<OpsmlServerError>)> {
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
            &exchange_token,
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
) -> Result<Json<BinnedCustomMetrics>, (StatusCode, Json<OpsmlServerError>)> {
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
            &exchange_token,
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

/// Get drift  profiles for UI
/// UI will make a request to return all profiles for a given card
/// The card is identified by parent drift path.
/// All profiles will be downloaded, decrypted and returned to the UI in the DriftProfile enum
#[instrument(skip_all)]
pub async fn get_drift_profiles_for_ui(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<RawFileRequest>,
) -> DriftProfileResult {
    if !perms.has_read_permission() {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        internal_server_error(e, "Failed to create temp dir")
    })?;
    let lpath = tmp_dir.path();
    let rpath = PathBuf::from(&req.path);

    download_artifacts(
        state.storage_client.clone(),
        state.sql_client.clone(),
        lpath,
        &rpath,
        &req.registry_type.to_string(),
        Some(&req.uid),
    )
    .await
    .map_err(|e| {
        error!("Failed to download artifact: {}", e);
        internal_server_error(e, "Failed to download artifact")
    })?;

    let profiles = load_drift_profiles(lpath).map_err(|e| {
        error!("Failed to load drift profile: {}", e);
        internal_server_error(e, "Failed to load drift profile")
    })?;

    Ok(Json(profiles))
}

/// Get drift alerts
pub async fn get_drift_alerts(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftAlertRequest>,
) -> Result<Json<Alerts>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_read_permission() {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {}", e);
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::Alerts,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift alerts: {}", e);
            internal_server_error(e, "Failed to get drift alerts")
        })?;

    let status_code = response.status();

    match status_code.is_success() {
        true => {
            let body = response.json::<Alerts>().await.map_err(|e| {
                error!("Failed to parse scouter response: {}", e);
                internal_server_error(e, "Failed to parse scouter response")
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {}", e);
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

#[instrument(skip_all)]
pub async fn check_scouter_health(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
) -> Result<Json<Alive>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {}", e);
        internal_server_error(e, "Failed to exchange token for scouter")
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
            error!("Failed to get scouter healthcheck: {}", e);
            internal_server_error(e, "Failed to get scouter healthcheck")
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<Alive>().await.map_err(|e| {
                error!("Failed to parse scouter response: {}", e);
                internal_server_error(e, "Failed to parse scouter response")
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {}", e);
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/scouter/profile", prefix),
                post(insert_drift_profile).put(update_drift_profile),
            )
            .route(
                &format!("{}/scouter/profile/ui", prefix),
                post(get_drift_profiles_for_ui),
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
            .route(&format!("{}/scouter/alerts", prefix), get(get_drift_alerts))
            .route(
                &format!("{}/scouter/healthcheck", prefix),
                get(check_scouter_health),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter router");
            Err(anyhow::anyhow!("Failed to create scouter router"))
                .context("Panic occurred while creating the router")
        }
    }
}
