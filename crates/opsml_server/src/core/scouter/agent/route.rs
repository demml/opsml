use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post},
};
use opsml_auth::permission::UserPermissions;
use opsml_types::api::RequestType;

use opsml_client::error::ApiClientError;
use scouter_client::{
    AgentEvalTaskRequest, AgentEvalTaskResponse, AgentEvalWorkflowPaginationResponse,
    EvalRecordPaginationRequest, EvalRecordPaginationResponse,
};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::debug;
use tracing::{error, instrument};

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/agent/page/record",
    request_body(content = inline(serde_json::Value), description = "Eval record pagination request"),
    responses(
        (status = 200, description = "Paginated agent eval records", body = inline(serde_json::Value)),
        (status = 404, description = "Not found", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn query_agent_eval_records(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<EvalRecordPaginationRequest>,
) -> Result<Json<EvalRecordPaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !data.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    debug!("Getting agent eval records with params: {:?}", &body);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let request = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize request: {e}");
        internal_server_error(e, "Failed to serialize request", None)
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::AgentRecords,
            RequestType::Post,
            Some(request),
            None,
            None,
            &exchange_token,
        )
        .await;

    let response = match response {
        Ok(resp) => resp,
        Err(e) => {
            if let ApiClientError::RequestError(ref req_err) = e
                && req_err.status() == Some(StatusCode::NOT_FOUND)
            {
                error!("Agent records not found: {e}");
                return Err(internal_server_error(
                    e,
                    "Agent records not found",
                    Some(StatusCode::NOT_FOUND),
                ));
            }

            error!("Failed to get agent records: {e}");
            return Err(internal_server_error(
                e,
                "Failed to get agent records",
                None,
            ));
        }
    };

    let body = response
        .json::<EvalRecordPaginationResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse agent records: {e}");
            internal_server_error(e, "Failed to parse agent records", None)
        })?;

    Ok(Json(body))
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/agent/page/workflow",
    request_body(content = inline(serde_json::Value), description = "Eval record pagination request for workflow"),
    responses(
        (status = 200, description = "Paginated agent eval workflow records", body = inline(serde_json::Value)),
        (status = 404, description = "Not found", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn query_agent_eval_workflow(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<EvalRecordPaginationRequest>,
) -> Result<Json<AgentEvalWorkflowPaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !data.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    debug!("Getting agent eval workflow with params: {:?}", &body);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let request = serde_json::to_value(&body).map_err(|e| {
        error!("Failed to serialize request: {e}");
        internal_server_error(e, "Failed to serialize request", None)
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::AgentWorkflow,
            RequestType::Post,
            Some(request),
            None,
            None,
            &exchange_token,
        )
        .await;

    let response = match response {
        Ok(resp) => resp,
        Err(e) => {
            if let ApiClientError::RequestError(ref req_err) = e
                && req_err.status() == Some(StatusCode::NOT_FOUND)
            {
                error!("Agent workflow not found: {e}");
                return Err(internal_server_error(
                    e,
                    "Agent workflow not found",
                    Some(StatusCode::NOT_FOUND),
                ));
            }

            error!("Failed to get agent workflow: {e}");
            return Err(internal_server_error(
                e,
                "Failed to get agent workflow",
                None,
            ));
        }
    };

    let body = response
        .json::<AgentEvalWorkflowPaginationResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse agent workflow: {e}");
            internal_server_error(e, "Failed to parse agent workflow", None)
        })?;

    Ok(Json(body))
}

#[utoipa::path(
    get,
    path = "/opsml/api/scouter/agent/task",
    params(
        ("name" = String, Query, description = "Eval task name"),
        ("space" = String, Query, description = "Space the task belongs to"),
        ("version" = String, Query, description = "Task version"),
    ),
    responses(
        (status = 200, description = "Agent eval task response", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_agent_tasks(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<AgentEvalTaskRequest>,
) -> Result<Json<AgentEvalTaskResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !data.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    debug!("Getting agent task with params: {:?}", &params);
    let exchange_token = data.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string", None)
    })?;

    let response = data
        .scouter_client
        .request(
            scouter::Routes::AgentTask,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get agent task: {e}");
            internal_server_error(e, "Failed to get agent task", None)
        })?;

    let body = response
        .json::<AgentEvalTaskResponse>()
        .await
        .map_err(|e| {
            error!("Failed to parse agent task: {e}");
            internal_server_error(e, "Failed to parse agent task", None)
        })?;

    Ok(Json(body))
}

pub async fn get_scouter_agent_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/scouter/agent/task"),
                get(get_agent_tasks),
            )
            .route(
                &format!("{prefix}/scouter/agent/page/workflow"),
                post(query_agent_eval_workflow),
            )
            .route(
                &format!("{prefix}/scouter/agent/page/record"),
                post(query_agent_eval_records),
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
