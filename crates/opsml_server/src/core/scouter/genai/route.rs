use crate::core::error::{internal_server_error, OpsmlServerError};
use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_types::api::RequestType;

use tracing::debug;

use scouter_client::{
    GenAIEvalRecordPaginationRequest, GenAIEvalRecordPaginationResponse, GenAIEvalTaskRequest,
    GenAIEvalTaskResponse, GenAIEvalWorkflowPaginationResponse,
};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn query_genai_eval_records(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAIEvalRecordPaginationRequest>,
) -> Result<Json<GenAIEvalRecordPaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    debug!("Getting genai eval records with params: {:?}", &body);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let request = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize request: {e}");
        internal_server_error(e, "Failed to serialize request")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::GenAIRecords,
            RequestType::Post,
            Some(request),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai records: {e}");
            internal_server_error(e, "Failed to get genai records")
        })?;

    let body = response
        .json::<GenAIEvalRecordPaginationResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse genai records: {e}");
            internal_server_error(e, "Failed to parse genai records")
        })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn query_genai_eval_workflow(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAIEvalRecordPaginationRequest>,
) -> Result<Json<GenAIEvalWorkflowPaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    debug!("Getting genai eval workflow with params: {:?}", &body);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter")
    })?;

    let request = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize request: {e}");
        internal_server_error(e, "Failed to serialize request")
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::GenAIWorkflow,
            RequestType::Post,
            Some(request),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai workflow: {e}");
            internal_server_error(e, "Failed to get genai workflow")
        })?;

    let body = response
        .json::<GenAIEvalWorkflowPaginationResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse genai workflow: {e}");
            internal_server_error(e, "Failed to parse genai workflow")
        })?;

    Ok(Json(body))
}

#[instrument(skip_all)]
pub async fn get_genai_tasks(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<GenAIEvalTaskRequest>,
) -> Result<Json<GenAIEvalTaskResponse>, (StatusCode, Json<OpsmlServerError>)> {
    // validate time window
    debug!("Getting genai task with params: {:?}", &params);
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
            scouter::Routes::GenAITask,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai task: {e}");
            internal_server_error(e, "Failed to get genai task")
        })?;

    // extract body into SpcDriftFeatures

    let body = response
        .json::<GenAIEvalTaskResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse genai task: {e}");
            internal_server_error(e, "Failed to parse genai task")
        })?;

    Ok(Json(body))
}

pub async fn get_scouter_genai_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/scouter/genai/task"),
                get(get_genai_tasks),
            )
            .route(
                &format!("{prefix}/scouter/genai/page/workflow"),
                post(query_genai_eval_workflow),
            )
            .route(
                &format!("{prefix}/scouter/genai/page/record"),
                post(query_genai_eval_records),
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
