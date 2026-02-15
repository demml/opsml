use crate::error::RegistryError;
use crate::registries::client::artifact::ArtifactExt;
use crate::registries::client::base::Registry;
use crate::registries::client::card::{CardRegistry, ClientCardRegistry, ScouterRegistry};
use opsml_semver::VersionType;
use opsml_settings::ScouterSettings;
use opsml_settings::config::OpsmlMode;
use opsml_state::{app_state, get_api_client};
use opsml_types::contracts::{ArtifactKey, CardArgs, DeleteCardRequest};
use opsml_types::contracts::{CardQueryArgs, CardRecord, CreateCardResponse};
use opsml_types::*;
use scouter_client::{
    ProfileRequest, ProfileStatusRequest, RegisteredProfileResponse, ScouterClient,
};
use tracing::{debug, error, instrument};

#[cfg(feature = "server")]
use crate::registries::server::card::ServerCardRegistry;

pub fn setup_scouter_client(
    settings: &ScouterSettings,
) -> Result<Option<ScouterClient>, RegistryError> {
    if settings.server_uri.is_empty() {
        debug!("Scouter client is disabled");
        return Ok(None);
    }

    // Create a new HTTP client with default config
    let scouter_client = ScouterClient::new(None)?;
    Ok(Some(scouter_client))
}

/// Parent enum for handling Card client/server logic
#[derive(Debug, Clone)]
pub enum OpsmlCardRegistry {
    Client(ClientCardRegistry),

    #[cfg(feature = "server")]
    Server(ServerCardRegistry),
}

impl OpsmlCardRegistry {
    #[instrument(skip_all)]
    pub fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let state = &app_state();
        let mode = &*state.mode()?;

        match mode {
            OpsmlMode::Client => {
                let api_client = get_api_client().clone();

                let client_registry = ClientCardRegistry::new(registry_type, api_client)?;
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

                    // check if scouter is enabled
                    let scouter_client = setup_scouter_client(&config.scouter_settings)?;

                    // TODO (steven): Why clone config when we could use app state directly in server registry?
                    let server_registry = state.block_on(async {
                        ServerCardRegistry::new(
                            registry_type,
                            settings,
                            db_settings,
                            scouter_client,
                        )
                        .await
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

    pub fn list_cards(&self, args: &CardQueryArgs) -> Result<Vec<CardRecord>, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.list_cards(args)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.list_cards(args).await })
            }
        }
    }

    pub fn check_card_uid(&self, uid: &str) -> Result<bool, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.check_uid_exists(uid)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.check_uid_exists(uid).await })
            }
        }
    }

    pub fn create_card(
        &self,
        card: CardRecord,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        match self {
            Self::Client(client_registry) => {
                Ok(client_registry.create_card(card, version, version_type, pre_tag, build_tag)?)
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => app_state().block_on(async {
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
            Self::Client(client_registry) => {
                Ok(client_registry.get_artifact_key(uid, registry_type)?)
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => app_state()
                .block_on(async { server_registry.get_artifact_key(uid, registry_type).await }),
        }
    }

    #[instrument(skip_all)]
    pub fn get_key(&self, args: &CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        match self {
            Self::Client(client_registry) => {
                Ok(client_registry.get_key(args).inspect_err(|e| {
                    error!("Client - Failed to get key from: {e}");
                })?)
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async {
                    let key = server_registry.get_key(args).await.inspect_err(|e| {
                        error!("Failed to get key: {e}");
                    })?;

                    // convert to client ArtifactKey
                    Ok(ArtifactKey {
                        uid: key.uid,
                        space: key.space,
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
            Self::Client(client_registry) => Ok(client_registry.delete_card(delete_request)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.delete_card(delete_request).await })
            }
        }
    }

    pub fn update_card(&self, card: &CardRecord) -> Result<(), RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.update_card(card)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                app_state().block_on(async { server_registry.update_card(card).await })
            }
        }
    }

    /// Generic function to check the health of an integrated service
    ///
    /// # Arguments
    /// * `service` - The integrated service to check
    ///
    /// # Returns
    /// * `Result<bool, RegistryError>` - Ok if the service is healthy, Err if there was an error
    #[instrument(skip_all)]
    pub fn check_service_health(&self, service: IntegratedService) -> Result<bool, RegistryError> {
        match self {
            Self::Client(client_registry) => Ok(client_registry.check_service_health(service)?),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.check_service_health(service),
        }
    }

    pub fn update_drift_profile_status(
        &self,
        request: &ProfileStatusRequest,
    ) -> Result<(), RegistryError> {
        match self {
            Self::Client(client_registry) => {
                Ok(client_registry.update_drift_profile_status(request)?)
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => server_registry.update_drift_profile_status(request),
        }
    }

    /// Inserts a scouter profile into the registry when opsml is integrated with scouter
    ///
    /// # Arguments
    /// * `profile` - The profile to be inserted
    ///
    /// # Returns
    /// * `Result<(), RegistryError>` - Ok if the profile was inserted successfully, Err if there was an error
    #[instrument(skip_all)]
    pub fn insert_scouter_profile(
        &self,
        profile: &ProfileRequest,
    ) -> Result<RegisteredProfileResponse, RegistryError> {
        match self {
            Self::Client(client_registry) => {
                debug!("ClientRegistry: Inserting scouter profile");
                Ok(client_registry.insert_scouter_profile(profile)?)
            }
            #[cfg(feature = "server")]
            Self::Server(server_registry) => {
                debug!("ServerRegistry: Inserting scouter profile");
                server_registry.insert_scouter_profile(profile)
            }
        }
    }

    pub fn compare_card_hash(
        &self,
        content_hash: &[u8],
    ) -> Result<Option<CardArgs>, RegistryError> {
        match self {
            Self::Client(client_registry) => client_registry.compare_card_hash(content_hash),
            #[cfg(feature = "server")]
            Self::Server(server_registry) => app_state()
                .block_on(async { server_registry.compare_card_hash(content_hash).await }),
        }
    }
}
