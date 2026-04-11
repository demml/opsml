use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::state::AppState;
use axum::{
    Extension, Json,
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_types::{
    RegistryType,
    contracts::{InvokeRequest, InvokeResponse, Operation, ResourceType},
};
use std::sync::Arc;
use tracing::{error, instrument};

/// Synchronously invoke an agent by id.
///
/// POST /opsml/api/v1/agent/{id}/invoke
#[utoipa::path(
    post,
    path = "/opsml/api/v1/agent/{id}/invoke",
    params(
        ("id" = String, Path, description = "Agent ID to invoke"),
    ),
    request_body = InvokeRequest,
    responses(
        (status = 200, description = "Agent invocation result", body = InvokeResponse),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 404, description = "Agent not found", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "agentic"
)]
#[instrument(skip_all)]
pub async fn invoke_agent(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(id): Path<String>,
    Json(body): Json<InvokeRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<OpsmlServerError>)> {
    if !state.agent_store.has(&id) {
        return Err((
            StatusCode::NOT_FOUND,
            Json(OpsmlServerError::not_found(&format!("Agent '{id}'"))),
        ));
    }

    // Agents are server-side resources; require at minimum an authenticated write-capable user.
    // Full space-based permission check is deferred until AgentStore exposes agent metadata.
    if !perms.has_write_permission("") {
        return Err((
            StatusCode::FORBIDDEN,
            Json(OpsmlServerError::permission_denied()),
        ));
    }

    let input = match body.input.as_str() {
        Some(s) => s.to_string(),
        None => body.input.to_string(),
    };

    let invoke_response = state.agent_store.invoke(&id, &input).await.map_err(|e| {
        error!("Agent invoke failed for {id}: {e}");
        internal_server_error(e, "Agent invocation failed", None)
    })?;

    let mut response = Json(invoke_response).into_response();
    response.extensions_mut().insert(AuditContext {
        resource_id: id.clone(),
        resource_type: ResourceType::Card,
        metadata: format!("agent_id={id} user={}", perms.username),
        operation: Operation::Create,
        registry_type: Some(RegistryType::SubAgent),
        access_location: None,
    });
    Ok(response)
}

/// Poll the status of an async agent job.
///
/// GET /opsml/api/v1/agent/{id}/jobs/{job_id}
#[utoipa::path(
    get,
    path = "/opsml/api/v1/agent/{id}/jobs/{job_id}",
    params(
        ("id" = String, Path, description = "Agent ID"),
        ("job_id" = String, Path, description = "Job ID to poll"),
    ),
    responses(
        (status = 200, description = "Job status and result", body = InvokeResponse),
        (status = 403, description = "Forbidden", body = OpsmlServerError),
        (status = 404, description = "Job not found", body = OpsmlServerError),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "agentic"
)]
#[instrument(skip_all)]
pub async fn get_agent_job(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path((_id, job_id)): Path<(String, String)>,
) -> Result<impl IntoResponse, (StatusCode, Json<OpsmlServerError>)> {
    let job = state.agent_store.get_job(&job_id).await.ok_or_else(|| {
        (
            StatusCode::NOT_FOUND,
            Json(OpsmlServerError::not_found(&format!("Job '{job_id}'"))),
        )
    })?;

    if job.owner != perms.username && !perms.group_permissions.contains(&"admin".to_string()) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(OpsmlServerError::permission_denied()),
        ));
    }

    let invoke_response = InvokeResponse {
        job_id: job.id,
        status: job.status,
        result: job.result,
        metadata: opsml_types::contracts::InvokeMetadata {
            agent_id: job.agent_id.clone(),
            invocation: "async".to_string(),
            duration_ms: job.duration_ms,
        },
    };

    let mut response = Json(invoke_response).into_response();
    response.extensions_mut().insert(AuditContext {
        resource_id: job_id.clone(),
        resource_type: ResourceType::Card,
        metadata: format!("job_id={job_id} user={}", perms.username),
        operation: Operation::Read,
        registry_type: Some(RegistryType::SubAgent),
        access_location: None,
    });
    Ok(response)
}
