use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::files::utils::download_artifacts;
use crate::core::scouter;

use crate::core::scouter::types::DriftProfileResult;
use crate::core::scouter::utils::load_drift_profiles;
use crate::core::scouter::utils::save_encrypted_profile;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post, put},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_sql::base::SqlClient;
use opsml_types::api::RequestType;
use opsml_types::contracts::Operation;
use opsml_types::contracts::ResourceType;
use opsml_types::contracts::{DriftProfileRequest, UpdateProfileRequest};
use opsml_types::Alive;
use reqwest::Response;
use tracing::debug;

use scouter_client::{
    Alerts, BinnedMetrics, BinnedPsiFeatureMetrics, DriftAlertRequest, DriftRequest,
    LLMDriftRecordPaginationRequest, ProfileRequest, ProfileStatusRequest,
    RegisteredProfileResponse, ScouterResponse, ScouterServerError, SpcDriftFeatures,
    UpdateAlertResponse, UpdateAlertStatus,
};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tempfile::tempdir;
use tracing::{error, info, instrument};

async fn parse_scouter_response(
    response: Response,
) -> Result<Json<ScouterResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let status_code = response.status();

    match status_code.is_success() {
        true => {
            let body = response.json::<ScouterResponse>().await.map_err(|e| {
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

pub async fn insert_drift_profile(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileRequest>,
) -> Result<Json<RegisteredProfileResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    info!("Inserting drift profile for space: {:?}", &body.space);

    let profile = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize profile request: {e}");
        internal_server_error(e, "Failed to serialize profile request")
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
            internal_server_error(e, "Failed to insert drift profile")
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
            internal_server_error(e, "Failed to get artifact key")
        })?;

    let drift_path = artifact_key.storage_path().join(&req.profile_uri);

    // list files in the directory
    let files = state.storage_client.find(&drift_path).await.map_err(|e| {
        error!("Failed to list files in directory: {e}");
        internal_server_error(e, "Failed to list files in directory")
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
        internal_server_error(e, "Failed to get encryption key")
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
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::Profile,
            RequestType::Put,
            Some(serde_json::to_value(&req.request).map_err(|e| {
                error!("Failed to serialize profile request: {e}");
                internal_server_error(e, "Failed to serialize profile request")
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile: {e}");
            internal_server_error(e, "Failed to update drift profile")
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
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let mut response = data
        .scouter_client
        .request(
            scouter::Routes::ProfileStatus,
            RequestType::Put,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize profile status request: {e}");
                internal_server_error(e, "Failed to serialize profile status request")
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to update drift profile status: {e}");
            internal_server_error(e, "Failed to update drift profile status")
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

#[instrument(skip(data, params))]
pub async fn get_spc_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<SpcDriftFeatures>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
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
            error!("Failed to get drift features: {e}");
            internal_server_error(e, "Failed to get drift features")
        })?;

    let body = response.json::<SpcDriftFeatures>().await.map_err(|e| {
        error!("Failed to parse drift features: {e}");
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
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
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
            error!("Failed to get drift features: {e}");
            internal_server_error(e, "Failed to get drift features")
        })?;

    // extract body into SpcDriftFeatures

    let body = response
        .json::<BinnedPsiFeatureMetrics>()
        .await
        .map_err(|e| {
            error!("Failed to parse drift features: {e}");
            internal_server_error(e, "Failed to parse drift features")
        })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_custom_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedMetrics>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window

    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
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
            error!("Failed to get drift features: {e}");
            internal_server_error(e, "Failed to get drift features")
        })?;

    // extract body into SpcDriftFeatures
    let body = response.json::<BinnedMetrics>().await.map_err(|e| {
        error!("Failed to parse drift features: {e}");
        internal_server_error(e, "Failed to parse drift features")
    })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_llm_drift(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedMetrics>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window
    debug!("Getting LLM drift features with params: {:?}", &params);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::DriftLLM,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift features: {e}");
            internal_server_error(e, "Failed to get drift features")
        })?;

    // extract body into SpcDriftFeatures

    let body = response.json::<BinnedMetrics>().await.map_err(|e| {
        error!("Failed to parse drift features: {e}");
        internal_server_error(e, "Failed to parse drift features")
    })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_llm_drift_records(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<LLMDriftRecordPaginationRequest>,
) -> Result<Json<PaginationResponse<LLMDriftServerRecord>>, (StatusCode, Json<ScouterServerError>)>
{
    debug!("Getting LLM drift features with params: {:?}", &params);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::DriftLLM,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get drift features: {e}");
            internal_server_error(e, "Failed to get drift features")
        })?;
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
            internal_server_error(e, "Failed to get artifact key")
        })?;

    if !perms.has_read_permission(&artifact_key.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    // create temp dir
    let tmp_dir = tempdir().map_err(|e| {
        error!("Failed to create temp dir: {e}");
        internal_server_error(e, "Failed to create temp dir")
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
            internal_server_error("No profiles found", "No profiles found")
        })?
        .root_dir;

    // Create destination subdirectory inside temp_dir
    let dest_path = tmp_dir.path().join(source_path);

    std::fs::create_dir_all(&dest_path).map_err(|e| {
        error!("Failed to create directory: {e}");
        internal_server_error(e, "Failed to create directory")
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
        internal_server_error(e, "Failed to download artifact")
    })?;

    let profiles = load_drift_profiles(tmp_path, &req.drift_profile_uri_map).map_err(|e| {
        error!("Failed to load drift profile: {e}");
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
    if !perms.has_read_permission(&params.space) {
        return OpsmlServerError::permission_denied().into_response(StatusCode::FORBIDDEN);
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
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
            error!("Failed to get drift alerts: {e}");
            internal_server_error(e, "Failed to get drift alerts")
        })?;

    let status_code = response.status();

    match status_code.is_success() {
        true => {
            let body = response.json::<Alerts>().await.map_err(|e| {
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
            error!("Failed to get scouter healthcheck: {e}");
            internal_server_error(e, "Failed to get scouter healthcheck")
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let _ = response.json::<Alive>().await.map_err(|e| {
                error!("Failed to parse scouter response: {e}");
                internal_server_error(e, "Failed to parse scouter response")
            })?;
            Ok(Json(Alive { alive: true }))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response")
            })?;
            // return error response
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn get_scouter_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
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
            .route(&format!("{prefix}/scouter/drift/spc"), get(get_spc_drift))
            .route(&format!("{prefix}/scouter/drift/psi"), get(get_psi_drift))
            .route(
                &format!("{prefix}/scouter/drift/custom"),
                get(get_custom_drift),
            )
            .route(&format!("{prefix}/scouter/drift/llm"), get(get_llm_drift))
            .route(
                &format!("{prefix}/scouter/alerts"),
                get(get_drift_alerts).put(update_alert_status),
            )
            .route(
                &format!("{prefix}/scouter/healthcheck"),
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
