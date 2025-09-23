use crate::core::error::{internal_server_error, OpsmlServerError};

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::get,
    Json, Router,
};

use opsml_events::AuditContext;

use opsml_sql::error::SqlError;

use opsml_sql::traits::*;
use opsml_types::contracts::*;
use opsml_types::RegistryType;

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;

use tracing::{debug, error};

pub async fn list_mcp_servers(
    State(state): State<Arc<AppState>>,
    Query(params): Query<ServiceQueryArgs>,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    debug!("Getting recent mcp services with params: {:?}", &params);

    let servers = state
        .sql_client
        .get_recent_services(&params)
        .await
        .map_err(|e| {
            error!("Failed to get unique space names: {e}");
            internal_server_error(e, "Failed to get unique space names")
        })?;

    let audit_context = AuditContext {
        resource_id: "list_mcp_servers".to_string(),
        resource_type: ResourceType::Database,
        metadata: params.get_metadata(),
        registry_type: Some(RegistryType::Service),
        operation: Operation::List,
        access_location: None,
    };

    let mcp_servers: Result<Vec<McpServer>, SqlError> =
        servers.iter().map(|s| s.to_mcp_server()).collect();

    match mcp_servers {
        Ok(servers) => {
            let response = Json(McpServers { servers }).into_response();

            let mut response = response;
            response.extensions_mut().insert(audit_context);
            Ok(response)
        }
        Err(e) => {
            error!("Failed to convert service to MCP server: {e}");
            Err(internal_server_error(
                e,
                "Failed to convert service to MCP server",
            ))
        }
    }
}

pub async fn get_llm_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(&format!("{prefix}/llm/mcp/servers"), get(list_mcp_servers))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create mcp router");
            // panic
            Err(anyhow::anyhow!("Failed to create mcp router"))
                .context("Panic occurred while creating the router")
        }
    }
}
