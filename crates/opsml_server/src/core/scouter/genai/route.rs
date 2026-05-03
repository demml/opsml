use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::scouter;
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::{Path, Query, State},
    http::StatusCode,
    routing::{get, post},
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_types::api::RequestType;
use opsml_types::contracts::{Operation, ResourceType};
use scouter_client::{
    AgentActivityQuery, AgentDashboardRequest, AgentDashboardResponse, ConversationQuery,
    GenAiAgentActivityResponse, GenAiDashBoardReqeust, GenAiDashboardResponse,
    GenAiErrorBreakdownResponse, GenAiMetricsRequest, GenAiModelUsageResponse,
    GenAiOperationBreakdownResponse, GenAiSpanFilters, GenAiSpansResponse,
    GenAiTokenMetricsResponse, GenAiToolActivityResponse, GenAiTraceMetricsRequest,
    GenAiTraceMetricsResponse, ScouterServerError, ToolDashboardRequest, ToolDashboardResponse,
};
use serde::Serialize;
use serde::de::DeserializeOwned;
use std::collections::HashMap;

use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

async fn post_proxy<Req, Res>(
    state: &Arc<AppState>,
    perms: &UserPermissions,
    route: scouter::Routes,
    body: &Req,
    query_string: Option<String>,
    error_context: &str,
) -> Result<Json<Res>, (StatusCode, Json<OpsmlServerError>)>
where
    Req: Serialize + ?Sized,
    Res: DeserializeOwned,
{
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = state
        .scouter_client
        .request(
            route,
            RequestType::Post,
            Some(serde_json::to_value(body).map_err(|e| {
                error!("Failed to serialize request body: {e}");
                internal_server_error(e, "Failed to serialize request body", None)
            })?),
            query_string,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to {error_context}: {e}");
            let message = format!("Failed to {error_context}");
            internal_server_error(e, &message, None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: error_context.to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<Res>().await.map_err(|e| {
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

async fn post_proxy_with_path<Req, Res>(
    state: &Arc<AppState>,
    perms: &UserPermissions,
    route: scouter::Routes,
    path_segments: &[&str],
    body: &Req,
    error_context: &str,
) -> Result<Json<Res>, (StatusCode, Json<OpsmlServerError>)>
where
    Req: Serialize + ?Sized,
    Res: DeserializeOwned,
{
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = state
        .scouter_client
        .request_with_path(
            route,
            path_segments,
            RequestType::Post,
            Some(serde_json::to_value(body).map_err(|e| {
                error!("Failed to serialize request body: {e}");
                internal_server_error(e, "Failed to serialize request body", None)
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to {error_context}: {e}");
            let message = format!("Failed to {error_context}");
            internal_server_error(e, &message, None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: error_context.to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<Res>().await.map_err(|e| {
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

fn is_valid_conversation_id(id: &str) -> bool {
    !id.is_empty()
        && id.len() <= 200
        && id
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | ':' | '.' | '/'))
}

fn is_valid_trace_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 128 && id.chars().all(|c| c.is_ascii_hexdigit())
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/tokens",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    responses(
        (status = 200, description = "GenAI token metrics", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_token_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiTokenMetricsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiTokenMetrics,
        &body,
        None,
        "get genai token metrics",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/operations",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    responses(
        (status = 200, description = "GenAI operation breakdown", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_operations(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiOperationBreakdownResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiOperations,
        &body,
        None,
        "get genai operations",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/models",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    responses(
        (status = 200, description = "GenAI model usage", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_models(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiModelUsageResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiModels,
        &body,
        None,
        "get genai model usage",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/agents",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    params(
        ("agent_name" = Option<String>, Query, description = "Optional agent name"),
    ),
    responses(
        (status = 200, description = "GenAI agent activity", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_agents(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<AgentActivityQuery>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiAgentActivityResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string", None)
    })?;

    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiAgents,
        &body,
        if query_string.is_empty() {
            None
        } else {
            Some(query_string)
        },
        "get genai agent activity",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/tools",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    responses(
        (status = 200, description = "GenAI tool activity", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_tools(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiToolActivityResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiTools,
        &body,
        None,
        "get genai tool activity",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/metrics/errors",
    request_body(content = inline(serde_json::Value), description = "GenAI metrics request"),
    responses(
        (status = 200, description = "GenAI error breakdown", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_errors(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiMetricsRequest>,
) -> Result<Json<GenAiErrorBreakdownResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiErrors,
        &body,
        None,
        "get genai error breakdown",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/spans",
    request_body(content = inline(serde_json::Value), description = "GenAI span filter request"),
    responses(
        (status = 200, description = "GenAI spans", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_spans(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiSpanFilters>,
) -> Result<Json<GenAiSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiSpans,
        &body,
        None,
        "get genai spans",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/agent/metrics",
    request_body(content = inline(serde_json::Value), description = "GenAI agent dashboard request"),
    responses(
        (status = 200, description = "GenAI agent dashboard", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_agent_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<AgentDashboardRequest>,
) -> Result<Json<AgentDashboardResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiAgentMetrics,
        &body,
        None,
        "get genai agent dashboard",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/tool/metrics",
    request_body(content = inline(serde_json::Value), description = "GenAI tool dashboard request"),
    responses(
        (status = 200, description = "GenAI tool dashboard", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_tool_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ToolDashboardRequest>,
) -> Result<Json<ToolDashboardResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiToolMetrics,
        &body,
        None,
        "get genai tool dashboard",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/dashboard",
    request_body(content = inline(serde_json::Value), description = "GenAI composite dashboard request"),
    responses(
        (status = 200, description = "GenAI composite dashboard", body = inline(serde_json::Value)),
        (status = 400, description = "Invalid request", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_dashboard(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<GenAiDashboardRequest>,
) -> Result<Json<GenAiDashboardResponse>, (StatusCode, Json<OpsmlServerError>)> {
    post_proxy(
        &state,
        &perms,
        scouter::Routes::GenAiDashboard,
        &body,
        None,
        "get genai dashboard",
    )
    .await
}

#[utoipa::path(
    post,
    path = "/opsml/api/scouter/genai/traces/{id}/metrics",
    params(
        ("id" = String, Path, description = "Trace ID (hex-encoded)"),
    ),
    request_body(content = inline(serde_json::Value), description = "Trace-scoped GenAI metrics request"),
    responses(
        (status = 200, description = "Trace-scoped GenAI metrics", body = inline(serde_json::Value)),
        (status = 400, description = "Invalid trace id", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_trace_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(id): Path<String>,
    Json(body): Json<GenAiTraceMetricsRequest>,
) -> Result<Json<GenAiTraceMetricsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !is_valid_trace_id(&id) {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::new(
                "Invalid trace id format (expected hex string)".to_string(),
            )),
        ));
    }

    post_proxy_with_path(
        &state,
        &perms,
        scouter::Routes::GenAiTraceMetrics,
        &[id.as_str(), "metrics"],
        &body,
        "get genai trace metrics",
    )
    .await
}

#[utoipa::path(
    get,
    path = "/opsml/api/scouter/genai/conversation/{id}",
    params(
        ("id" = String, Path, description = "Conversation ID"),
        ("start_time" = Option<String>, Query, description = "Optional conversation window start time"),
        ("end_time" = Option<String>, Query, description = "Optional conversation window end time"),
    ),
    responses(
        (status = 200, description = "GenAI conversation spans", body = inline(serde_json::Value)),
        (status = 400, description = "Invalid conversation id", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn genai_conversation(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(id): Path<String>,
    Query(params): Query<ConversationQuery>,
) -> Result<Json<GenAiSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    if !is_valid_conversation_id(&id) {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::new(
                "Invalid conversation id format".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string", None)
    })?;

    let mut response = state
        .scouter_client
        .request_with_path(
            scouter::Routes::GenAiConversation,
            &[id.as_str()],
            RequestType::Get,
            None,
            if query_string.is_empty() {
                None
            } else {
                Some(query_string)
            },
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get genai conversation: {e}");
            internal_server_error(e, "Failed to get genai conversation", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: id.to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<GenAiSpansResponse>().await.map_err(|e| {
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

pub async fn get_scouter_genai_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/scouter/genai/metrics/tokens"),
                post(genai_token_metrics),
            )
            .route(
                &format!("{prefix}/scouter/genai/metrics/operations"),
                post(genai_operations),
            )
            .route(
                &format!("{prefix}/scouter/genai/metrics/models"),
                post(genai_models),
            )
            .route(
                &format!("{prefix}/scouter/genai/metrics/agents"),
                post(genai_agents),
            )
            .route(
                &format!("{prefix}/scouter/genai/metrics/tools"),
                post(genai_tools),
            )
            .route(
                &format!("{prefix}/scouter/genai/metrics/errors"),
                post(genai_errors),
            )
            .route(&format!("{prefix}/scouter/genai/spans"), post(genai_spans))
            .route(
                &format!("{prefix}/scouter/genai/conversation/{{id}}"),
                get(genai_conversation),
            )
            .route(
                &format!("{prefix}/scouter/genai/agent/metrics"),
                post(genai_agent_metrics),
            )
            .route(
                &format!("{prefix}/scouter/genai/tool/metrics"),
                post(genai_tool_metrics),
            )
            .route(
                &format!("{prefix}/scouter/genai/dashboard"),
                post(genai_dashboard),
            )
            .route(
                &format!("{prefix}/scouter/genai/traces/{{id}}/metrics"),
                post(genai_trace_metrics),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter genai router");
            Err(anyhow::anyhow!("Failed to create scouter genai router"))
                .context("Panic occurred while creating the genai router")
        }
    }
}
