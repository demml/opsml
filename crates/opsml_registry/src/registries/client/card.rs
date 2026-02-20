use crate::error::RegistryError;
use crate::registries::client::artifact::ArtifactExt;
use crate::registries::client::base::ErrorResponse;
use crate::registries::client::base::Registry;
use opsml_client::OpsmlApiClient;
use opsml_client::error::ApiClientError;
use opsml_semver::VersionType;
use opsml_types::{Alive, IntegratedService, RegistryType, api::*, cards::CardTable, contracts::*};
use scouter_client::RegisteredProfileResponse;
use scouter_client::{ProfileRequest, ProfileStatusRequest, ScouterServerError};
use std::sync::Arc;
use tracing::{debug, error, instrument};

#[derive(Debug, Clone)]
pub struct ClientCardRegistry {
    registry_type: RegistryType,
    pub api_client: Arc<OpsmlApiClient>,
}

impl ClientCardRegistry {
    pub fn new(
        registry_type: RegistryType,
        api_client: Arc<OpsmlApiClient>,
    ) -> Result<Self, RegistryError> {
        Ok(Self {
            registry_type,
            api_client,
        })
    }
}

impl Registry for ClientCardRegistry {
    fn client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }
    fn table_name(&self) -> String {
        CardTable::from_registry_type(&self.registry_type).to_string()
    }

    fn registry_type(&self) -> &RegistryType {
        &self.registry_type
    }
}

pub trait CardRegistry: Registry {
    #[instrument(skip_all)]
    fn list_cards(&self, args: &CardQueryArgs) -> Result<Vec<CardRecord>, RegistryError> {
        let query_string = serde_qs::to_string(&args)?;

        let response = self
            .client()
            .request(
                Routes::CardList,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to list cards {}", e);
            })?;

        response
            .json::<Vec<CardRecord>>()
            .map_err(RegistryError::RequestError)
    }

    #[instrument(skip_all)]
    fn create_card(
        &self,
        card: CardRecord,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        // create version request
        let version_request = CardVersionRequest {
            name: card.name().to_string(),
            space: card.space().to_string(),
            version,
            version_type,
            pre_tag,
            build_tag,
        };

        // create card request
        let card_request = CreateCardRequest {
            card,
            registry_type: self.registry_type().clone(),
            version_request,
        };

        debug!(
            "Creating card with name: {}, space: {}, registry type: {:?}",
            card_request.card.name(),
            card_request.card.space(),
            card_request.registry_type,
        );

        let body = serde_json::to_value(card_request).inspect_err(|e| {
            error!("Failed to serialize card request {}", e);
        })?;

        let response = self
            .client()
            .request(
                Routes::CardCreate,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to create card {}", e);
            })?;

        // check if 403 forbidden and get error message
        if response.status() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(RegistryError::RequestError)?;

            return Err(ApiClientError::ForbiddenError(error.error).into());
        }

        let created = response
            .json::<CreateCardResponse>()
            .map_err(RegistryError::RequestError)?;

        if created.registered {
            Ok(created)
        } else {
            error!("Failed to create card");
            Err(RegistryError::CreateCardError)
        }
    }

    #[instrument(skip_all)]
    fn update_card(&self, card: &CardRecord) -> Result<(), RegistryError> {
        let update_request = UpdateCardRequest {
            card: card.clone(),
            registry_type: self.registry_type().clone(),
        };

        // serialize card to json
        let body = serde_json::to_value(update_request).inspect_err(|e| {
            error!("Failed to serialize update request {}", e);
        })?;

        let response = self.client().request(
            Routes::CardUpdate,
            RequestType::Post,
            Some(body),
            None,
            None,
        )?;

        // check if 403 forbidden and get error message
        if response.status() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(RegistryError::RequestError)?;

            return Err(ApiClientError::ForbiddenError(error.error).into());
        }

        let updated = response.json::<UpdateCardResponse>().inspect_err(|e| {
            error!("Failed to parse update card response {}", e);
        })?;

        if updated.updated {
            Ok(())
        } else {
            Err(RegistryError::UpdateCardError)
        }
    }

    #[instrument(skip_all)]
    fn delete_card(&self, delete_request: DeleteCardRequest) -> Result<(), RegistryError> {
        let query_string = serde_qs::to_string(&delete_request)?;

        let response = self
            .client()
            .request(
                Routes::CardDelete,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Request failed {}", e);
            })?;

        // check if 403 forbidden and get error message
        if response.status() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(RegistryError::RequestError)?;

            return Err(ApiClientError::ForbiddenError(error.error).into());
        }

        let deleted = response
            .json::<UidResponse>()
            .map_err(RegistryError::RequestError)?;

        if !deleted.exists {
            Ok(())
        } else {
            Err(RegistryError::DeleteCardError)
        }
    }

    #[instrument(skip_all)]
    fn check_uid_exists(&self, uid: &str) -> Result<bool, RegistryError> {
        let uid_request = UidRequest {
            uid: uid.to_string(),
            registry_type: self.registry_type().clone(),
        };
        let query_string = serde_qs::to_string(&uid_request)?;

        let response = self
            .client()
            .request(
                Routes::Card,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to check uid exists {}", e);
            })?;

        let exists = response
            .json::<UidResponse>()
            .map_err(RegistryError::RequestError)?;

        Ok(exists.exists)
    }

    #[instrument(skip_all)]
    fn get_key(&self, args: &CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        let query_string = serde_qs::to_string(&args)?;
        let response = self
            .client()
            .request(
                Routes::CardLoad,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get artifact key {}", e);
            })?;

        Ok(response.json::<ArtifactKey>()?)
    }

    #[instrument(skip_all)]
    fn compare_card_hash(&self, content_hash: &[u8]) -> Result<Option<CardArgs>, RegistryError> {
        let hash_request = CompareHashRequest {
            registry_type: self.registry_type().clone(),
            content_hash: content_hash.to_vec(),
        };

        let body = serde_json::to_value(&hash_request)?;

        let response = self
            .client()
            .request(
                Routes::CardCompareHash,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to compare card hash {}", e);
            })?;

        let hash_response = response.json::<CompareHashResponse>()?;

        Ok(hash_response.card)
    }
}

pub trait ScouterRegistry: Registry {
    #[instrument(skip_all)]
    fn check_service_health(&self, service: IntegratedService) -> Result<bool, RegistryError> {
        let route = match service {
            IntegratedService::Scouter => Routes::ScouterHealthcheck,
            // Add other service routes as needed
        };

        let response = self
            .client()
            .request(route, RequestType::Get, None, None, None)
            .inspect_err(|e| {
                error!("Failed to check {} service health: {}", service, e);
            })?;

        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        let alive = response
            .json::<Alive>()
            .map_err(RegistryError::RequestError)?;

        Ok(alive.alive)
    }

    fn insert_scouter_profile(
        &self,
        profile: &ProfileRequest,
    ) -> Result<RegisteredProfileResponse, RegistryError> {
        let body = serde_json::to_value(profile)?;

        let response = self
            .client()
            .request(
                Routes::ScouterProfile,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert scouter profile {}", e);
            })?;

        // check response status for error
        if response.status() == 500 {
            // raise error
            let error = response
                .json::<ScouterServerError>()
                .map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ForbiddenError(error.error).into());
        }

        // check for any other errors
        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        let registered_profile = response
            .json::<RegisteredProfileResponse>()
            .map_err(RegistryError::RequestError)?;

        Ok(registered_profile)
    }

    fn update_drift_profile_status(
        &self,
        profile: &ProfileStatusRequest,
    ) -> Result<(), RegistryError> {
        let body = serde_json::to_value(profile)?;

        let response = self
            .client()
            .request(
                Routes::ScouterProfileStatus,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to update scouter profile status {}", e);
            })?;

        // check response status for error
        if response.status() == 500 {
            // raise error
            let error = response
                .json::<ScouterServerError>()
                .map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ForbiddenError(error.error).into());
        }

        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        Ok(())
    }
}

impl CardRegistry for ClientCardRegistry {}
impl ScouterRegistry for ClientCardRegistry {}
impl ArtifactExt for ClientCardRegistry {}
