use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::files::utils::download_artifacts;
use crate::core::scouter;

use crate::core::scouter::types::DriftProfileResult;
use crate::core::scouter::utils::load_drift_profiles;
use crate::core::scouter::utils::parse_scouter_response;
use crate::core::scouter::utils::save_encrypted_profile;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::State,
    http::StatusCode,
    routing::{post, put},
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_sql::traits::ArtifactLogicTrait;
use opsml_types::api::RequestType;
use opsml_types::contracts::Operation;
use opsml_types::contracts::ResourceType;
use opsml_types::contracts::{DriftProfileRequest, UpdateProfileRequest};

use scouter_client::{
    ProfileRequest, ProfileStatusRequest, RegisteredProfileResponse, ScouterResponse,
    ScouterServerError,
};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{error, info, instrument};

pub async fn insert_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileRequest>,
) -> Result<Json<RegisteredProfileResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    info!("Inserting drift profile for space: {:?}", &body.space);

    let profile = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize profile request: {e}");
        internal_server_error(e, "Failed to serialize profile request", None)
    })?;

    let mut response = state
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
            error!("Failed to insert drift profile: {e}");
            internal_server_error(e, "Failed to insert drift profile", None)
        })?;

    let metadata = serde_json::json!({
        "space": body.space,
        "drift_type": body.drift_type.to_string(),
    });
    let metadata = serde_json::to_string(&metadata)
        .unwrap_or_else(|e| format!("Failed to serialize ProfileRequest: {e}"));

    let audit_context = AuditContext {
        resource_id: "insert_drift".to_string(),
        resource_type: ResourceType::Drift,
        metadata,
        registry_type: None,
        operation: Operation::Create,
        access_location: None,
    };

    response.extensions_mut().insert(audit_context);

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response
                .json::<RegisteredProfileResponse>()
                .await
                .map_err(|e| {
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

    let artifact_key = state
        .sql_client
        .get_artifact_key(&req.uid, &req.registry_type.to_string())
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {e}");
            internal_server_error(e, "Failed to get artifact key", None)
        })?;

    let drift_path = artifact_key.storage_path().join(&req.profile_uri);

    // list files in the directory
    let files = state.storage_client.find(&drift_path).await.map_err(|e| {
        error!("Failed to list files in directory: {e}");
        internal_server_error(e, "Failed to list files in directory", None)
    })?;

    // assert files is not empty
    if files.is_empty() {
        error!("No files found in directory");
        return OpsmlServerError::no_files_found().into_response(StatusCode::NOT_FOUND);
    }

    // get first file
    let filename = drift_path
        .file_name()
        .and_then(|f| f.to_str())
        .ok_or_else(|| {
            error!("Failed to get filename from path");
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::no_drift_profile_found()),
            )
        })?;

    let encryption_key = artifact_key.get_decrypt_key().map_err(|e| {
        error!("Failed to get encryption key: {e}");
        internal_server_error(e, "Failed to get encryption key", None)
    })?;

    save_encrypted_profile(
        &req.request.profile,
        filename,
        &encryption_key,
        &state.storage_client,
        &drift_path,
    )
    .await?;

    // 2. Scouter task
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::Profile,
            RequestType::Put,
            Some(serde_json::to_value(&req.request).map_err(|e| {
                error!("Failed to serialize profile request: {e}");
                internal_server_error(e, "Failed to serialize profile request", None)
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile: {e}");
            internal_server_error(e, "Failed to update drift profile", None)
        })?;

    info!("Drift profile updated successfully for uid: {:?}", &req.uid);

    let metadata = serde_json::json!({
        "space": req.request.space,
        "drift_type": req.request.drift_type.to_string(),
    });
    let metadata = serde_json::to_string(&metadata)
        .unwrap_or_else(|e| format!("Failed to serialize ProfileRequest: {e}"));

    let audit_context = AuditContext {
        resource_id: "update_drift".to_string(),
        resource_type: ResourceType::Drift,
        metadata,
        registry_type: None,
        operation: Operation::Update,
        access_location: Some(req.profile_uri.clone()),
    };

    response.extensions_mut().insert(audit_context);

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
#[instrument(skip_all)]
pub async fn update_drift_profile_status(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileStatusRequest>,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !perms.has_write_permission(&body.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }
    info!("Updating drift profile status: {:?}", &body);

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = data
        .scouter_client
        .request(
            scouter::Routes::ProfileStatus,
            RequestType::Put,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize profile status request: {e}");
                internal_server_error(e, "Failed to serialize profile status request", None)
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile status: {e}");
            internal_server_error(e, "Failed to update drift profile status", None)
        })?;

    let metadata = serde_json::json!({
        "name": body.name,
        "space": body.space,
        "version": body.version,
        "active": body.active,
        "drift_type": body.drift_type.as_ref().map(|dt| dt.to_string()),
        "deactivate_others": body.deactivate_others,
    });
    let metadata = serde_json::to_string(&metadata)
        .unwrap_or_else(|e| format!("Failed to serialize ProfileStatusRequest: {e}"));

    let audit_context = AuditContext {
        resource_id: "update_drift_status".to_string(),
        resource_type: ResourceType::Drift,
        metadata,
        registry_type: None,
        operation: Operation::Update,
        access_location: None,
    };

    response.extensions_mut().insert(audit_context);

    parse_scouter_response(response).await
}

/// Get drift  profiles for UI
/// UI will make a request to return all profiles for a given card
/// The card is identified by parent drift path.
/// All profiles will be downloaded, decrypted and returned to the UI in the DriftProfile enum
#[instrument(skip_all)]
pub async fn get_drift_profiles_for_ui(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<DriftProfileRequest>,
) -> DriftProfileResult {
    // get artifact key for the given uid
    let registry = req.registry_type.to_string();
    let artifact_key = state
        .sql_client
        .get_artifact_key(&req.uid, &registry)
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {e}");
            internal_server_error(e, "Failed to get artifact key", None)
        })?;

    if !perms.has_read_permission(&artifact_key.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir", None)
    })?;
    let tmp_path = tmp_dir.path();

    // extract root dir from first profile
    // Get source path (where files live in storage)
    let source_path = &req
        .drift_profile_uri_map
        .values()
        .next()
        .ok_or_else(|| {
            error!("No profiles found");
            internal_server_error(
                "No profiles found",
                "No profiles found",
                Some(StatusCode::NOT_FOUND),
            )
        })?
        .root_dir;

    // Create destination subdirectory inside temp_dir
    let dest_path = tmp_dir.path().join(source_path);

    std::fs::create_dir_all(&dest_path).map_err(|e| {
        error!("Failed to create directory: {e}");
        internal_server_error(e, "Failed to create directory", None)
    })?;

    download_artifacts(
        state.storage_client.clone(),
        state.sql_client.clone(),
        &dest_path,
        source_path,
        &registry,
        Some(&req.uid),
    )
    .await
    .map_err(|e| {
        error!("Failed to download artifact: {e}");
        internal_server_error(e, "Failed to download artifact", None)
    })?;

    let profiles = load_drift_profiles(tmp_path, &req.drift_profile_uri_map).map_err(|e| {
        error!("Failed to load drift profile: {e}");
        internal_server_error(e, "Failed to load drift profile", None)
    })?;

    Ok(Json(profiles))
}

pub async fn get_scouter_profile_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/scouter/profile"),
                post(insert_drift_profile).put(update_drift_profile),
            )
            .route(
                &format!("{prefix}/scouter/profile/ui"),
                post(get_drift_profiles_for_ui),
            )
            .route(
                &format!("{prefix}/scouter/profile/status"),
                put(update_drift_profile_status),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter profile router");
            Err(anyhow::anyhow!("Failed to create scouter profile router"))
                .context("Panic occurred while creating the profile router")
        }
    }
}
