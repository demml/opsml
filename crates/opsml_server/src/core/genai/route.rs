use crate::core::error::{OpsmlServerError, internal_server_error};

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Json, Router,
    extract::{OriginalUri, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::get,
};

use opsml_events::AuditContext;

use opsml_sql::error::SqlError;

use opsml_sql::traits::*;
use opsml_types::RegistryType;
use opsml_types::contracts::*;

use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;

use tracing::{debug, error};

pub async fn list_mcp_servers(
    State(state): State<Arc<AppState>>,
    // ServiceQueryArgs contains a tags param array which needs to be parsed correctly
    OriginalUri(uri): OriginalUri,
) -> Result<Response, (StatusCode, Json<OpsmlServerError>)> {
    let params: ServiceQueryArgs = match uri.query() {
        Some(query) => serde_qs::from_str(query).map_err(|e| {
            error!("Failed to parse query string: {e}");
            internal_server_error(e, "Failed to parse query string")
        })?,
        None => {
            return Err(internal_server_error(
                "No query string found",
                "No query string found",
            ));
        }
    };

    debug!("Getting recent mcp services with params: {:?}", &params);

    let servers = state
        .sql_client
        .get_recent_services(&params)
        .await
        .map_err(|e| {
            error!("Failed to list mcp servers: {e}");
            internal_server_error(e, "Failed to list mcp servers")
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

pub async fn get_genai_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{prefix}/genai/mcp/servers"),
            get(list_mcp_servers),
        )
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
