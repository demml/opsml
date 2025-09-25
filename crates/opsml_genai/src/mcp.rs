use opsml_registry::registries::genai::OpsmlGenAIRegistry;

use crate::error::LLMError;
use opsml_types::contracts::McpServers;
use opsml_types::contracts::{ServiceQueryArgs, ServiceType};
use pyo3::prelude::*;
use tracing::error;

#[pyfunction]
#[pyo3(signature = (space=None, name=None, tags=None))]
pub fn list_mcp_servers(
    space: Option<String>,
    name: Option<String>,
    tags: Option<Vec<String>>,
) -> Result<McpServers, LLMError> {
    // need to a separate method to get the latest MCP services
    let registry = OpsmlGenAIRegistry::new()?;
    let args = ServiceQueryArgs {
        space: space.clone(),
        name: name.clone(),
        tags: tags.clone(),
        service_type: ServiceType::Mcp,
    };

    let servers = registry
        .list_mcp_servers(&args)
        .inspect_err(|e| error!("Failed to list MCP servers: {e}"))?;

    Ok(servers)
}
