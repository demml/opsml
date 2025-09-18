use opsml_settings::config::OpsmlStorageSettings;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_types::{RegistryMode, RegistryType};
use scouter_client::ScouterClient;
use std::sync::Arc;

/// Base trait for server registries providing common functionality
pub trait Registry {
    /// Get reference to the SQL client
    fn sql_client(&self) -> &Arc<SqlClientEnum>;

    /// Get the registry mode (always Server for server registries)
    fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    /// Get the table name as string
    fn table_name(&self) -> String;

    /// Get the registry type
    fn registry_type(&self) -> &RegistryType;

    /// Get storage settings
    fn storage_settings(&self) -> &OpsmlStorageSettings;

    /// Get scouter client if available
    fn scouter_client(&self) -> Option<&ScouterClient>;
}
