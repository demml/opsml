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

use opsml_types::api::RequestType;

use tracing::debug;

use scouter_client::{BinnedMetrics, BinnedPsiFeatureMetrics, DriftRequest, SpcDriftFeatures};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

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
pub async fn get_genai_task_metrics(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedMetrics>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window
    debug!("Getting genai task metrics with params: {:?}", &params);
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
            scouter::Routes::DriftGenAITask,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai task metrics: {e}");
            internal_server_error(e, "Failed to get genai task metrics")
        })?;

    // extract body into SpcDriftFeatures

    let body = response.json::<BinnedMetrics>().await.map_err(|e| {
        error!("Failed to parse genai task metrics: {e}");
        internal_server_error(e, "Failed to parse genai task metrics")
    })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_genai_workflow_metrics(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DriftRequest>,
) -> Result<Json<BinnedMetrics>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window
    debug!("Getting genai task metrics with params: {:?}", &params);
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
            scouter::Routes::DriftGenAIWorkflow,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai workflow metrics: {e}");
            internal_server_error(e, "Failed to get genai workflow metrics")
        })?;

    // extract body into SpcDriftFeatures

    let body = response.json::<BinnedMetrics>().await.map_err(|e| {
        error!("Failed to parse genai workflow metrics: {e}");
        internal_server_error(e, "Failed to parse genai workflow metrics")
    })?;

    Ok(Json(body))
}

pub async fn get_scouter_drift_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{prefix}/scouter/drift/spc"), get(get_spc_drift))
            .route(&format!("{prefix}/scouter/drift/psi"), get(get_psi_drift))
            .route(
                &format!("{prefix}/scouter/drift/custom"),
                get(get_custom_drift),
            )
            .route(
                &format!("{prefix}/scouter/drift/genai/task"),
                get(get_genai_task_metrics),
            )
            .route(
                &format!("{prefix}/scouter/drift/genai/workflow"),
                get(get_genai_workflow_metrics),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter drift router");
            Err(anyhow::anyhow!("Failed to create scouter drift router"))
                .context("Panic occurred while creating the router")
        }
    }
}
