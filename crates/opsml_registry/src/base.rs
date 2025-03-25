use opsml_client::ClientRegistry;
use opsml_error::error::RegistryError;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlMode;
use opsml_state::{app_state, get_api_client};
use opsml_types::contracts::{
    Card, CardQueryArgs, CreateCardResponse, GetMetricRequest, MetricRequest,
};
use opsml_types::*;
use opsml_types::{
    cards::{HardwareMetrics, Metric, Parameter},
    contracts::{
        ArtifactKey, DeleteCardRequest, GetHardwareMetricRequest, GetParameterRequest,
        HardwareMetricRequest, ParameterRequest,
    },
};
use tracing::{error, instrument};

#[derive(Debug, Clone)]
pub enum OpsmlRegistry {
    ClientRegistry(opsml_client::ClientRegistry),

    #[cfg(feature = "server")]
    ServerRegistry(crate::server::registry::server_logic::ServerRegistry),
}

/// OpsmlRegistry implementation that is called from the client by a user (either in client or server mode)
/// when interacting with card registries. Note - this is not used in the server itself, as the server relies
/// solely on the SqlClientEnum for sql operations. Given the non-async support of Pyo3 and python's
/// non-default async support, the happy path is to enable sync only calls from the client to the server when used in
/// client mode (ClientRegistry). If the user opts to put their local code into server mode, then
/// server OpsmlRegistry calls will make use of the app_state.runtime in order to interact with the ServerRegistry and underlying
/// SqlClientEnum.
///
impl OpsmlRegistry {
    #[instrument(skip_all)]
    pub fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let state = app_state();
        let mode = state.mode()?;

        match mode {
            OpsmlMode::Client => {
                let api_client = get_api_client().clone();
                let client_registry = ClientRegistry::new(registry_type, api_client)?;
                Ok(Self::ClientRegistry(client_registry))
            }
            OpsmlMode::Server => {
                #[cfg(feature = "server")]
                {
                    let config = state.config()?;
                    let settings = config.storage_settings().map_err(|e| {
                        error!("Failed to get storage settings: {}", e);
                        RegistryError::Error(format!(
                            "Failed to get storage settings with error: {}",
                            e
                        ))
                    })?;
                    let db_settings = config.database_settings.clone();
                    let server_registry = state.block_on(async {
                        crate::server::registry::server_logic::ServerRegistry::new(
                            registry_type,
                            settings,
                            db_settings,
                        )
                        .await
                    })?;
                    Ok(Self::ServerRegistry(server_registry))
                }
                #[cfg(not(feature = "server"))]
                {
                    error!("Server feature not enabled");
                    Err(RegistryError::Error(
                        "Server feature not enabled".to_string(),
                    ))
                }
            }
        }
    }

    pub fn mode(&self) -> RegistryMode {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.mode(),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => server_registry.mode(),
        }
    }

    pub fn table_name(&self) -> String {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.table_name(),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => server_registry.table_name(),
        }
    }

    pub fn list_cards(&self, args: CardQueryArgs) -> Result<Vec<Card>, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.list_cards(args),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.list_cards(args).await })
            }
        }
    }

    pub fn check_card_uid(&self, uid: &str) -> Result<bool, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.check_uid_exists(uid),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.check_uid_exists(uid).await })
            }
        }
    }

    pub fn create_card(
        &self,
        card: Card,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                client_registry.create_card(card, version, version_type, pre_tag, build_tag)
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => app_state().block_on(async {
                server_registry
                    .create_card(card, version, version_type, pre_tag, build_tag)
                    .await
            }),
        }
    }

    pub fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                client_registry.get_artifact_key(uid, registry_type)
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => app_state()
                .block_on(async { server_registry.get_artifact_key(uid, registry_type).await }),
        }
    }

    pub fn load_card(&self, args: CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.load_card(args),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async {
                    let key = server_registry.load_card(args).await?;

                    // convert to client ArtifactKey
                    Ok(ArtifactKey {
                        uid: key.uid,
                        registry_type: key.registry_type,
                        encrypted_key: key.encrypted_key,
                        storage_key: key.storage_key,
                    })
                })
            }
        }
    }

    pub fn delete_card(&self, delete_request: DeleteCardRequest) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.delete_card(delete_request),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.delete_card(delete_request).await })
            }
        }
    }

    pub fn update_card(&self, card: &Card) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.update_card(card),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.update_card(card).await })
            }
        }
    }

    pub fn insert_hardware_metrics(
        &self,
        metrics: HardwareMetricRequest,
    ) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                client_registry.insert_hardware_metrics(&metrics)
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => app_state()
                .block_on(async { server_registry.insert_hardware_metrics(&metrics).await }),
        }
    }

    pub fn get_hardware_metrics(
        &self,
        request: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.get_hardware_metrics(request),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.get_hardware_metrics(request).await })
            }
        }
    }

    pub fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.insert_metrics(metrics),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.insert_metrics(metrics).await })
            }
        }
    }

    pub fn get_metrics(&self, metrics: &GetMetricRequest) -> Result<Vec<Metric>, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.get_metrics(metrics),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.get_metrics(metrics).await })
            }
        }
    }

    pub fn insert_parameters(&self, parameters: &ParameterRequest) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.insert_parameters(parameters),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.insert_parameters(parameters).await })
            }
        }
    }

    pub fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => client_registry.get_parameters(parameters),
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                app_state().block_on(async { server_registry.get_parameters(parameters).await })
            }
        }
    }
}
