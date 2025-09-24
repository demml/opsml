use opsml_registry::registries::genai::OpsmlGenAIRegistry;

use crate::error::LLMError;
use opsml_types::contracts::McpServers;
use opsml_types::contracts::{ServiceQueryArgs, ServiceType};
use pyo3::prelude::*;
use tracing::error;

#[pyfunction]
pub fn list_mcp_servers(
    space: Option<String>,
    name: Option<String>,
    tags: Option<Vec<String>>,
) -> Result<McpServers, LLMError> {
    // need to a separate method to get the latest MCP services
    let registry = OpsmlGenAIRegistry::new()?;

    let servers = registry
        .list_mcp_servers(&ServiceQueryArgs {
            space,
            name,
            tags,
            service_type: Some(ServiceType::Mcp.to_string()),
        })
        .inspect_err(|e| error!("Failed to list MCP servers: {e}"))?;

    Ok(servers)
}
