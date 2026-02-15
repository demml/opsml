use crate::error::RegistryError;
use opsml_settings::DatabaseSettings;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_sql::enums::client::get_sql_client;
use opsml_sql::error::SqlError;
use opsml_sql::{enums::client::SqlClientEnum, traits::*};
use opsml_types::{cards::CardTable, contracts::*, *};
use std::sync::Arc;

#[derive(Debug)]
pub struct ServerGenAIRegistry {
    sql_client: Arc<SqlClientEnum>,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerGenAIRegistry {
    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    pub fn table_name(&self) -> String {
        self.table_name.to_string()
    }
    pub async fn new(
        storage_settings: OpsmlStorageSettings,
        database_settings: DatabaseSettings,
    ) -> Result<Self, RegistryError> {
        let sql_client = Arc::new(get_sql_client(&database_settings).await?);
        let table_name = CardTable::from_registry_type(&RegistryType::Service);

        Ok(Self {
            sql_client,
            table_name,
            storage_settings,
        })
    }

    pub async fn list_mcp_servers(
        &self,
        args: &ServiceQueryArgs,
    ) -> Result<McpServers, RegistryError> {
        let servers = self.sql_client.get_recent_services(args).await?;

        let mcp_servers: Result<Vec<McpServer>, SqlError> =
            servers.iter().map(|s| s.to_mcp_server()).collect();

        Ok(McpServers {
            servers: mcp_servers?,
        })
    }
}
