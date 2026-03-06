use crate::core::state::AppState;
use anyhow::Result;
use axum::{Extension, Json, Router, extract::State, response::IntoResponse, routing::post};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_mcp::protocol::JsonRpcRequest;
use opsml_types::contracts::{Operation, ResourceType};
use std::sync::Arc;
use tracing::instrument;

#[instrument(skip_all)]
async fn mcp_handler(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<JsonRpcRequest>,
) -> impl IntoResponse {
    let method_label = match &req.call {
        opsml_mcp::protocol::McpCall::Initialize(_) => "initialize",
        opsml_mcp::protocol::McpCall::ToolsList => "tools/list",
        opsml_mcp::protocol::McpCall::ToolsCall(_) => "tools/call",
        opsml_mcp::protocol::McpCall::Unknown(_) => "unknown",
    };

    let resp = state.mcp_handler.handle(req);

    let mut response = Json(resp).into_response();
    response.extensions_mut().insert(AuditContext {
        resource_id: perms.username,
        resource_type: ResourceType::Database,
        metadata: format!("MCP method: {method_label}"),
        operation: Operation::Read,
        registry_type: None,
        access_location: None,
    });

    response
}

pub async fn get_mcp_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    Ok(Router::new().route(&format!("{prefix}/mcp"), post(mcp_handler)))
}
