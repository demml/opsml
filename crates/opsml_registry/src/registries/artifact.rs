use crate::error::RegistryError;
use crate::registries::client::artifact::{ArtifactRegistry, ClientArtifactRegistry};
use crate::registries::client::base::Registry;

use opsml_settings::config::OpsmlMode;
use opsml_state::{app_state, get_api_client};
use opsml_types::contracts::{
    ArtifactQueryArgs, ArtifactRecord, ArtifactType, CreateArtifactResponse,
};
use opsml_types::*;
use tracing::{error, instrument};

#[cfg(feature = "server")]
use crate::registries::server::artifact::ServerArtifactRegistry;

#[derive(Debug)]
pub enum OpsmlArtifactRegistry {
    Client(ClientArtifactRegistry),

    #[cfg(feature = "server")]
    Server(ServerArtifactRegistry),
}
impl OpsmlArtifactRegistry {
    #[instrument(skip_all)]
    pub fn new() -> Result<Self, RegistryError> {
        let state = &app_state();
        let mode = &*state.mode()?;

        match mode {
            OpsmlMode::Client => {
                let api_client = get_api_client().clone();
                let client_registry = ClientArtifactRegistry::new(api_client)?;
                Ok(Self::Client(client_registry))
            }
            OpsmlMode::Server => {
                #[cfg(feature = "server")]
                {
                    let config = state.config()?;
                    let settings = config.storage_settings().inspect_err(|e| {
                        error!("Failed to get storage settings: {e}");
                    })?;

                    let db_settings = config.database_settings.clone();

                    // TODO (steven): Why clone config when we could use app state directly in server registry?
                    let server_registry = state.block_on(async {
                        ServerArtifactRegistry::new(settings, db_settings).await
                    })?;

                    Ok(Self::Server(server_registry))
                }
                #[cfg(not(feature = "server"))]
                {
                    error!("Server feature not enabled");
                    Err(RegistryError::ServerFeatureNotEnabled)
                }
            }
        }
    }

    pub fn mode(&self) -> RegistryMode {
        match self {
            Self::Client(client_registry) => client_registry.mode(),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.mode(),
        }
    }

    pub fn table_name(&self) -> String {
        match self {
            Self::Client(client_registry) => client_registry.table_name(),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.table_name(),
        }
    }

    pub fn log_artifact(
        &self,
        space: String,
        name: String,
        version: String,
        media_type: String,
        artifact_type: ArtifactType,
    ) -> Result<CreateArtifactResponse, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.log_artifact(
                space,
                name,
                version,
                media_type,
                artifact_type,
            )?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => app_state().block_on(async {
                server_registry
                    .log_artifact(space, name, version, media_type, artifact_type)
                    .await
            }),
        }
    }

    pub fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.query_artifacts(query_args)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.query_artifacts(query_args).await })
            }
        }
    }
}
