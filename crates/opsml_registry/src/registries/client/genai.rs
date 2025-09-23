use crate::error::RegistryError;
use crate::registries::client::base::Registry;
use opsml_client::error::ApiClientError;
use opsml_client::OpsmlApiClient;
use opsml_types::{api::*, cards::CardTable, contracts::*, RegistryType};
use std::sync::Arc;
use tracing::error;

#[derive(Debug, Clone)]
pub struct ClientGenAIRegistry {
    pub api_client: Arc<OpsmlApiClient>,
}

impl ClientGenAIRegistry {
    pub fn new(api_client: Arc<OpsmlApiClient>) -> Result<Self, RegistryError> {
        Ok(Self { api_client })
    }
}

impl Registry for ClientGenAIRegistry {
    fn client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }
    fn table_name(&self) -> String {
        CardTable::from_registry_type(&RegistryType::Service).to_string()
    }

    fn registry_type(&self) -> &RegistryType {
        &RegistryType::Service
    }
}

pub trait GenAIRegistry: Registry {
    fn list_mcp_servers(&self, args: &ServiceQueryArgs) -> Result<McpServers, RegistryError> {
        // Query artifacts from the registry
        let params = serde_qs::to_string(args)?;

        let response = self
            .client()
            .request(
                Routes::GenAiMcpServers,
                RequestType::Get,
                None,
                Some(params),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to list MCP servers: {}", e);
            })?;

        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        response
            .json::<McpServers>()
            .map_err(RegistryError::RequestError)
    }
}
