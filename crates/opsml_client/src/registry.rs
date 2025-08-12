use crate::error::RegistryError;
use crate::{base::*, error::ApiClientError};
use opsml_semver::VersionType;
use opsml_types::{
    api::*,
    cards::{CardTable, HardwareMetrics, Metric, Parameter},
    contracts::*,
    Alive, IntegratedService, RegistryMode, RegistryType,
};
use scouter_client::{ProfileRequest, ProfileStatusRequest, ScouterServerError};
use serde::Deserialize;
use std::sync::Arc;
use tracing::error;
use tracing::instrument;

// Define the error response struct that matches the JSON structure
#[derive(Debug, Deserialize)]
pub struct ErrorResponse {
    error: String,
}

// TODO: Add trait for client and server registry
#[derive(Debug, Clone)]
pub struct ClientRegistry {
    registry_type: RegistryType,
    pub api_client: Arc<OpsmlApiClient>,
}

impl ClientRegistry {
    pub fn new(
        registry_type: RegistryType,
        api_client: Arc<OpsmlApiClient>,
    ) -> Result<Self, RegistryError> {
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

    #[instrument(skip_all)]
    pub fn list_cards(&self, args: CardQueryArgs) -> Result<Vec<CardRecord>, RegistryError> {
        let query_string = serde_qs::to_string(&args)?;

        let response = self
            .api_client
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
    pub fn create_card(
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
            registry_type: self.registry_type.clone(),
            version_request,
        };

        let body = serde_json::to_value(card_request).inspect_err(|e| {
            error!("Failed to serialize card request {}", e);
        })?;

        let response = self
            .api_client
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
    pub fn update_card(&self, card: &CardRecord) -> Result<(), RegistryError> {
        let update_request = UpdateCardRequest {
            card: card.clone(),
            registry_type: self.registry_type.clone(),
        };

        // serialize card to json
        let body = serde_json::to_value(update_request)?;

        let response = self.api_client.request(
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

        let updated = response
            .json::<UpdateCardResponse>()
            .map_err(RegistryError::RequestError)?;

        if updated.updated {
            Ok(())
        } else {
            Err(RegistryError::UpdateCardError)
        }
    }

    #[instrument(skip_all)]
    pub fn delete_card(&self, delete_request: DeleteCardRequest) -> Result<(), RegistryError> {
        let query_string = serde_qs::to_string(&delete_request)?;

        let response = self
            .api_client
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
    pub fn get_key(&self, args: &CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        let query_string = serde_qs::to_string(&args)?;

        let response = self
            .api_client
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

        response
            .json::<ArtifactKey>()
            .map_err(RegistryError::RequestError)
    }

    #[instrument(skip_all)]
    pub fn check_uid_exists(&self, uid: &str) -> Result<bool, RegistryError> {
        let uid_request = UidRequest {
            uid: uid.to_string(),
            registry_type: self.registry_type.clone(),
        };
        let query_string = serde_qs::to_string(&uid_request)?;

        let response = self
            .api_client
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

    fn artifact_key(
        &self,
        uid: &str,
        registry_type: &RegistryType,
        route: Routes,
    ) -> Result<ArtifactKey, RegistryError> {
        let key_request = ArtifactKeyRequest {
            uid: uid.to_string(),
            registry_type: registry_type.clone(),
        };

        let query_string = serde_qs::to_string(&key_request)?;

        let response = self
            .api_client
            .request(route, RequestType::Get, None, Some(query_string), None)
            .inspect_err(|e| {
                error!("Failed to get artifact key {}", e);
            })?;

        let key = response
            .json::<ArtifactKey>()
            .map_err(RegistryError::RequestError)?;

        Ok(key)
    }

    pub fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        self.artifact_key(uid, registry_type, Routes::ArtifactKey)
    }

    pub fn insert_hardware_metrics(
        &self,
        metrics: &HardwareMetricRequest,
    ) -> Result<(), RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert hardware metrics {}", e);
            })?;

        let inserted = response
            .json::<HardwareMetricResponse>()
            .map_err(RegistryError::RequestError)?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertHardwareMetricError)
        }
    }

    pub fn get_hardware_metrics(
        &self,
        metrics: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        let query_string = serde_qs::to_string(metrics)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get hardware metrics {}", e);
            })?;

        response
            .json::<Vec<HardwareMetrics>>()
            .map_err(RegistryError::RequestError)
    }

    pub fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert metrics {}", e);
            })?;

        let inserted = response
            .json::<MetricResponse>()
            .map_err(RegistryError::RequestError)?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertMetricError)
        }
    }

    pub fn get_metrics(&self, metrics: &GetMetricRequest) -> Result<Vec<Metric>, RegistryError> {
        let body = serde_json::to_value(metrics)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentMetrics,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get metrics {}", e);
            })?;

        response
            .json::<Vec<Metric>>()
            .map_err(RegistryError::RequestError)
    }

    pub fn insert_parameters(&self, parameters: &ParameterRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(parameters)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentParameters,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to insert parameters {}", e);
            })?;

        let inserted = response.json::<ParameterResponse>()?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::InsertParameterError)
        }
    }

    pub fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        let body = serde_json::to_value(parameters)?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentParameters,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get parameters {}", e);
            })?;

        response
            .json::<Vec<Parameter>>()
            .map_err(RegistryError::RequestError)
    }

    #[instrument(skip_all)]
    pub fn check_service_health(&self, service: IntegratedService) -> Result<bool, RegistryError> {
        let route = match service {
            IntegratedService::Scouter => Routes::ScouterHealthcheck,
            // Add other service routes as needed
        };

        let response = self
            .api_client
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

    pub fn insert_scouter_profile(&self, profile: &ProfileRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(profile)?;

        let response = self
            .api_client
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

        Ok(())
    }

    pub fn update_drift_profile_status(
        &self,
        profile: &ProfileStatusRequest,
    ) -> Result<(), RegistryError> {
        let body = serde_json::to_value(profile)?;

        let response = self
            .api_client
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

    /// Insert an artifact record into the opsml_artifact_registry
    /// # Arguments
    /// * `space` - The space of the artifact
    /// * `name` - The name of the artifact
    /// * `version` - The version of the artifact
    /// * `filename` - The filename of the artifact
    /// * `media_type` - The media type of the artifact
    /// # Returns
    /// * `CreateArtifactResponse` - The response containing the created artifact record
    pub fn log_artifact(
        &self,
        space: String,
        name: String,
        version: String,
        media_type: String,
        artifact_type: ArtifactType,
    ) -> Result<CreateArtifactResponse, RegistryError> {
        let body = serde_json::to_value(CreateArtifactRequest {
            space,
            name,
            version,
            media_type,
            artifact_type,
        })?;

        let response = self
            .api_client
            .request(
                Routes::ArtifactRecord,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .inspect_err(|e| {
                error!("Failed to log artifact {}", e);
            })?;

        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        response
            .json::<CreateArtifactResponse>()
            .map_err(RegistryError::RequestError)
    }

    pub fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, RegistryError> {
        // Query artifacts from the registry
        let params = serde_qs::to_string(query_args)?;

        let response = self
            .api_client
            .request(
                Routes::ArtifactRecord,
                RequestType::Get,
                None,
                Some(params),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to query artifacts: {e}");
            })?;

        if response.status() != 200 {
            let error_text = response.text().map_err(RegistryError::RequestError)?;
            return Err(ApiClientError::ServerError(error_text).into());
        }

        response
            .json::<Vec<ArtifactRecord>>()
            .map_err(RegistryError::RequestError)
    }
}
