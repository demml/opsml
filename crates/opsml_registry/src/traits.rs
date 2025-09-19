use crate::error::RegistryError;
use opsml_client::ClientRegistry;
use opsml_settings::OpsmlMode;
use opsml_state::{app_state, get_api_client};
use opsml_types::*;
use tracing::error;

pub trait Registry {
    fn new(registry_type: RegistryType) -> Result<Self, RegistryError>
    where
        Self: Sized,
    {
        let state = &app_state();
        let mode = &*state.mode()?;

        match mode {
            OpsmlMode::Client => Self::create_client_registry(registry_type),
            OpsmlMode::Server => Self::create_server_registry(registry_type),
        }
    }

    fn from_client_registry(client_registry: ClientRegistry) -> Result<Self, RegistryError>
    where
        Self: Sized;

    /// Create a new client registry instance
    /// # Arguments
    /// * `registry_type` - RegistryType
    /// # Returns
    /// Result<Self, RegistryError>
    fn create_client_registry(registry_type: RegistryType) -> Result<Self, RegistryError>
    where
        Self: Sized,
    {
        let api_client = get_api_client().clone();
        let client_registry = ClientRegistry::new(registry_type, api_client)?;
        Self::from_client_registry(client_registry)
    }

    #[cfg(feature = "server")]
    fn from_server_registry(
        server_registry: crate::server::registry::server_logic::ServerRegistry,
    ) -> Result<Self, RegistryError>
    where
        Self: Sized;

    /// Create a new server registry instance
    /// # Arguments
    /// * `registry_type` - RegistryType
    /// # Returns
    /// Result<Self, RegistryError>
    #[cfg(feature = "server")]
    fn create_server_registry(registry_type: RegistryType) -> Result<Self, RegistryError>
    where
        Self: Sized,
    {
        let state = &app_state();
        let config = state.config()?;

        let settings = config.storage_settings().inspect_err(|e| {
            error!("Failed to get storage settings: {e}");
        })?;

        let db_settings = config.database_settings.clone();

        let server_registry = state.block_on(async {
            crate::server::registry::server_logic::ServerRegistry::new(
                registry_type,
                settings,
                db_settings,
                None, // registry
            )
            .await
        })?;

        Self::from_server_registry(server_registry)
    }

    fn mode(&self) -> RegistryMode;
}
