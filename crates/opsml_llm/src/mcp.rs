use opsml_registry::registries::card::OpsmlCardRegistry;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::RegistryType;
use pyo3::prelude::*;

use crate::error::LLMError;
#[pyfunction]
pub fn list_mcp_servers(
    space: Option<String>,
    name: Option<String>,
    version: Option<String>,
    tags: Option<Vec<String>>,
) -> Result<Vec<String>, LLMError> {
    // need to a separate method to get the latest MCP services
    let registry = OpsmlCardRegistry::new(RegistryType::Service).unwrap();

    registry
        .list_cards(&CardQueryArgs {
            space,
            name,
            version,
            uid: None,
            limit: None,
            tags,
            max_date: None,
            sort_by_timestamp: Some(true),
            service_type: None,
            registry_type: RegistryType::Service,
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    // Placeholder implementation
    Ok(vec![
        "MCP Service 1".to_string(),
        "MCP Service 2".to_string(),
        "MCP Service 3".to_string(),
    ])
}
