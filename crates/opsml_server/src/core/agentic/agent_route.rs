use crate::core::error::{OpsmlServerError, internal_server_error};
use crate::core::state::AppState;
use axum::{
    Extension, Json,
    extract::{Path, State},
    http::StatusCode,
};
use opsml_auth::permission::UserPermissions;
use opsml_types::contracts::{InvokeRequest, InvokeResponse};
use std::sync::Arc;
use tracing::{error, instrument};

/// Synchronously invoke an agent by id.
///
/// POST /opsml/api/v1/agent/{id}/invoke
#[instrument(skip_all)]
pub async fn invoke_agent(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
    Path(id): Path<String>,
    Json(body): Json<InvokeRequest>,
) -> Result<Json<InvokeResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.agent_store.has(&id) {
        return Err((
            StatusCode::NOT_FOUND,
            Json(OpsmlServerError {
                error: format!("Agent not found: {id}"),
            }),
        ));
    }

    let input = match body.input.as_str() {
        Some(s) => s.to_string(),
        None => body.input.to_string(),
    };

    let response = state.agent_store.invoke(&id, &input).await.map_err(|e| {
        error!("Agent invoke failed for {id}: {e}");
        internal_server_error(e, "Agent invocation failed", None)
    })?;

    Ok(Json(response))
}

/// Poll the status of an async agent job.
///
/// GET /opsml/api/v1/agent/{id}/jobs/{job_id}
#[instrument(skip_all)]
pub async fn get_agent_job(
    State(state): State<Arc<AppState>>,
    Extension(_perms): Extension<UserPermissions>,
    Path((_id, job_id)): Path<(String, String)>,
) -> Result<Json<InvokeResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let job = state.agent_store.get_job(&job_id).await.ok_or_else(|| {
        (
            StatusCode::NOT_FOUND,
            Json(OpsmlServerError {
                error: format!("Job not found: {job_id}"),
            }),
        )
    })?;

    Ok(Json(InvokeResponse {
        job_id: job.id,
        status: job.status,
        result: job.result,
        metadata: opsml_types::contracts::InvokeMetadata {
            agent_id: job.agent_id.clone(),
            invocation: "async".to_string(),
            duration_ms: job.duration_ms,
        },
    }))
}
