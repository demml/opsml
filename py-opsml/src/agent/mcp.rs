use opsml_registry::registries::agent::OpsmlAgentRegistry;

use opsml_types::contracts::McpServers;
use opsml_types::contracts::{ServiceQueryArgs, ServiceType};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use tracing::error;

#[pyfunction]
#[pyo3(signature = (space=None, name=None, tags=None))]
pub fn list_mcp_servers(
    space: Option<String>,
    name: Option<String>,
    tags: Option<Vec<String>>,
) -> PyResult<McpServers> {
    let registry = OpsmlAgentRegistry::new().map_err(|e| {
        let msg = e.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    })?;
    let args = ServiceQueryArgs {
        space: space.clone(),
        name: name.clone(),
        tags: tags.clone(),
        service_type: ServiceType::Mcp,
    };

    registry.list_mcp_servers(&args).map_err(|e| {
        let msg = e.to_string();
        error!("{msg}");
        PyRuntimeError::new_err(msg)
    })
}
