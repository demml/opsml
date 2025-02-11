use opsml_error::error::RegistryError;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_types::contracts::{Card, CardQueryArgs};
use opsml_types::*;

#[derive(Debug)]
pub enum OpsmlRegistry {
    ClientRegistry(opsml_client::ClientRegistry),

    #[cfg(feature = "server")]
    ServerRegistry(crate::server::registry::server_logic::ServerRegistry),
}

impl OpsmlRegistry {
    pub async fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let config = OpsmlConfig::default();

        let storage_settings = config.storage_settings()?;
        match storage_settings.client_mode {
            true => {
                let client_registry =
                    opsml_client::ClientRegistry::new(&config, registry_type).await?;
                Ok(Self::ClientRegistry(client_registry))
            }
            #[cfg(feature = "server")]
            false => {
                let server_registry = crate::server::registry::server_logic::ServerRegistry::new(
                    &config,
                    registry_type,
                )
                .await?;
                Ok(Self::ServerRegistry(server_registry))
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

    pub async fn list_cards(&mut self, args: CardQueryArgs) -> Result<Vec<Card>, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                let cards = client_registry.list_cards(args).await?;
                Ok(cards)
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                let cards = server_registry.list_cards(args).await?;
                Ok(cards)
            }
        }
    }

    pub async fn check_card_uid(&mut self, uid: &str) -> Result<bool, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                let exists = client_registry.check_uid_exists(uid).await?;
                Ok(exists)
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                let exists = server_registry.check_uid_exists(uid).await?;
                Ok(exists)
            }
        }
    }

    pub async fn get_next_version(
        &mut self,
        name: &str,
        repository: &str,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<String, RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                client_registry
                    .get_next_version(name, repository, version, version_type, pre_tag, build_tag)
                    .await
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                server_registry
                    .get_next_version(name, repository, version, version_type, pre_tag, build_tag)
                    .await
            }
        }
    }

    pub async fn create_card(&mut self, card: Card) -> Result<(), RegistryError> {
        match self {
            Self::ClientRegistry(client_registry) => {
                client_registry.create_card(card).await?;
                Ok(())
            }
            #[cfg(feature = "server")]
            Self::ServerRegistry(server_registry) => {
                server_registry.create_card(card).await?;
                Ok(())
            }
        }
    }
}
