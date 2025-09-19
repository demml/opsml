// Attempting to start separating out different registry types and eventually aggregate then as an enum for
// OpsmlRegistry

use crate::error::RegistryError;
use opsml_client::ClientRegistry;

use crate::traits::Registry;
use opsml_types::*;

#[derive(Debug, Clone)]
pub enum EvaluationRegistry {
    ClientRegistry(opsml_client::ClientRegistry),

    #[cfg(feature = "server")]
    ServerRegistry(crate::server::registry::server_logic::ServerRegistry),
}

impl Registry for EvaluationRegistry {
    fn from_client_registry(client_registry: ClientRegistry) -> Result<Self, RegistryError>
    where
        Self: Sized,
    {
        Ok(Self::ClientRegistry(client_registry))
    }

    #[cfg(feature = "server")]
    fn from_server_registry(
        server_registry: crate::server::registry::server_logic::ServerRegistry,
    ) -> Result<Self, RegistryError>
    where
        Self: Sized,
    {
        Ok(EvaluationRegistry::ServerRegistry(server_registry))
    }

    fn mode(&self) -> RegistryMode {
        match self {
            EvaluationRegistry::ClientRegistry(reg) => reg.mode(),
            #[cfg(feature = "server")]
            EvaluationRegistry::ServerRegistry(reg) => reg.mode(),
        }
    }
}
