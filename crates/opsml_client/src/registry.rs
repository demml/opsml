use crate::base::*;
use crate::types::*;
use opsml_crypt::decrypt_key;
use opsml_error::error::RegistryError;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_types::cards::CardType;
use opsml_types::{cards::CardTable, contracts::*, RegistryMode, RegistryType};
use opsml_utils::uid_to_byte_key;
use tracing::instrument;
use tracing::{debug, error};

// TODO: Add trait for client and server registry
#[derive(Debug)]
pub struct ClientRegistry {
    registry_type: RegistryType,
    api_client: OpsmlApiClient,
}

impl ClientRegistry {
    pub async fn new(
        config: &OpsmlConfig,
        registry_type: RegistryType,
    ) -> Result<Self, RegistryError> {
        let storage_settings = config.storage_settings()?;
        let client = build_http_client(&storage_settings.api_settings)
            .map_err(|e| RegistryError::NewError(format!("Failed to create http client {}", e)))?;

        let api_client = OpsmlApiClient::new(&storage_settings, &client)
            .await
            .map_err(|e| RegistryError::NewError(format!("Failed to create http client {}", e)))?;

        Ok(Self {
            registry_type,
            api_client,
        })
    }

    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Client
    }

    pub fn table_name(&self) -> String {
        CardTable::from_registry_type(&self.registry_type).to_string()
    }

    pub async fn list_cards(&mut self, args: CardQueryArgs) -> Result<Vec<Card>, RegistryError> {
        // convert args struct to hasmap

        let args = ListCardRequest {
            uid: args.uid,
            name: args.name,
            repository: args.repository,
            version: args.version,
            max_date: args.max_date,
            tags: args.tags,
            limit: args.limit,
            sort_by_timestamp: args.sort_by_timestamp,
            registry_type: self.registry_type.clone(),
        };

        let query_string = serde_qs::to_string(&args)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request_with_retry(
                Routes::CardList,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to list cards {}", e)))?;

        response
            .json::<Vec<Card>>()
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to parse response {}", e)))
    }

    #[instrument(skip_all)]
    pub async fn create_card(
        &mut self,
        card: Card,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        // create version request
        let version_request = CardVersionRequest {
            name: card.name().to_string(),
            repository: card.repository().to_string(),
            version,
            version_type,
            pre_tag,
            build_tag,
        };

        // create card request
        let card_request = CreateCardRequest {
            card,
            registry_type: self.registry_type.clone(),
            version_request,
        };

        let body = serde_json::to_value(card_request).map_err(|e| {
            error!("Failed to serialize card request {}", e);
            RegistryError::Error(format!("Failed to serialize card {}", e))
        })?;

        let response = self
            .api_client
            .request_with_retry(
                Routes::CardCreate,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to create card {}", e);
                RegistryError::Error(format!("Failed to create card {}", e))
            })?;

        debug!("Response {:?}", response);

        let created = response
            .json::<CreateCardResponse>()
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to parse response {}", e)))?;

        if created.registered {
            Ok(created)
        } else {
            error!("Failed to create card");
            Err(RegistryError::Error("Failed to create card".to_string()))
        }
    }

    pub async fn update_card(&mut self, card: Card) -> Result<(), RegistryError> {
        // serialize card to json
        let body = serde_json::to_value(card).map_err(|e| {
            error!("Failed to serialize card {}", e);
            RegistryError::Error(format!("Failed to serialize card {}", e))
        })?;

        let response = self
            .api_client
            .request_with_retry(
                Routes::CardUpdate,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to update card {}", e)))?;

        let updated = response
            .json::<UpdateCardResponse>()
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to parse response {}", e)))?;

        if updated.updated {
            Ok(())
        } else {
            Err(RegistryError::Error("Failed to update card".to_string()))
        }
    }

    pub async fn delete_card(&mut self, uid: &str) -> Result<(), RegistryError> {
        let uid_request = UidRequest {
            uid: uid.to_string(),
            registry_type: self.registry_type.clone(),
        };
        let query_string = serde_qs::to_string(&uid_request)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request_with_retry(
                Routes::CardDelete,
                RequestType::Post,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to delete card {}", e)))?;

        let deleted = response
            .json::<UidResponse>()
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to parse response {}", e)))?;

        if !deleted.exists {
            Ok(())
        } else {
            Err(RegistryError::Error("Failed to delete card".to_string()))
        }
    }

    pub async fn check_uid_exists(&mut self, uid: &str) -> Result<bool, RegistryError> {
        let uid_request = UidRequest {
            uid: uid.to_string(),
            registry_type: self.registry_type.clone(),
        };
        let query_string = serde_qs::to_string(&uid_request)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request_with_retry(
                Routes::Card,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to check uid exists {}", e)))?;

        let exists = response
            .json::<UidResponse>()
            .await
            .map_err(|e| RegistryError::Error(format!("Failed to parse response {}", e)))?;

        Ok(exists.exists)
    }

    async fn artifact_key(
        &mut self,
        uid: &str,
        card_type: &CardType,
        route: Routes,
    ) -> Result<Vec<u8>, RegistryError> {
        let key_request = ArtifactKeyRequest {
            uid: uid.to_string(),
            card_type: card_type.clone(),
        };

        let query_string = serde_qs::to_string(&key_request).map_err(|e| {
            error!("Failed to serialize query args {}", e);
            RegistryError::Error(format!("Failed to serialize query args {}", e))
        })?;

        let response = self
            .api_client
            .request_with_retry(route, RequestType::Get, None, Some(query_string), None)
            .await
            .map_err(|e| {
                error!("Failed to get artifact key {}", e);
                RegistryError::Error(format!("Failed to get artifact key {}", e))
            })?;

        let key = response.json::<ArtifactKey>().await.map_err(|e| {
            error!("Failed to parse response {}", e);
            RegistryError::Error(format!("Failed to parse response {}", e))
        })?;

        let uid_key = uid_to_byte_key(uid)?;

        let decrypted_key = decrypt_key(&uid_key, &key.encrypted_key)?;

        Ok(decrypted_key)
    }

    pub async fn create_artifact_key(
        &mut self,
        uid: &str,
        card_type: &CardType,
    ) -> Result<Vec<u8>, RegistryError> {
        self.artifact_key(uid, card_type, Routes::Encrypt).await
    }

    pub async fn get_artifact_key(
        &mut self,
        uid: &str,
        card_type: &CardType,
    ) -> Result<Vec<u8>, RegistryError> {
        self.artifact_key(uid, card_type, Routes::Decrypt).await
    }
}
