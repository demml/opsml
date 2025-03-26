use crate::base::*;
use crate::types::*;
use opsml_error::error::RegistryError;
use opsml_semver::VersionType;
use opsml_types::cards::HardwareMetrics;
use opsml_types::{
    cards::{CardTable, Metric, Parameter},
    contracts::*,
    RegistryMode, RegistryType,
};
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

    pub fn list_cards(&self, args: CardQueryArgs) -> Result<Vec<Card>, RegistryError> {
        let query_string = serde_qs::to_string(&args)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request(
                Routes::CardList,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .map_err(|e| RegistryError::Error(format!("Failed to list cards {}", e)))?;

        response
            .json::<Vec<Card>>()
            .map_err(|e| RegistryError::Error(format!("Failed to parse card response {}", e)))
    }

    #[instrument(skip_all)]
    pub fn create_card(
        &self,
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
            .request(
                Routes::CardCreate,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to create card {}", e);
                RegistryError::Error(format!("Failed to create card {}", e))
            })?;

        // check if 403 forbidden and get error message
        if response.status().as_u16() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(|e| RegistryError::Error(format!("Failed to parse error response {e}")))?;

            return Err(RegistryError::Forbidden(error.error));
        }

        let created = response.json::<CreateCardResponse>().map_err(|e| {
            RegistryError::Error(format!("Failed to parse create card response {e}"))
        })?;

        if created.registered {
            Ok(created)
        } else {
            error!("Failed to create card");
            Err(RegistryError::Error("Failed to create card".to_string()))
        }
    }

    pub fn update_card(&self, card: &Card) -> Result<(), RegistryError> {
        let update_request = UpdateCardRequest {
            card: card.clone(),
            registry_type: self.registry_type.clone(),
        };

        // serialize card to json
        let body = serde_json::to_value(update_request).map_err(|e| {
            error!("Failed to serialize card {}", e);
            RegistryError::Error(format!("Failed to serialize card {e}"))
        })?;

        let response = self.api_client.request(
            Routes::CardUpdate,
            RequestType::Post,
            Some(body),
            None,
            None,
        )?;

        // check if 403 forbidden and get error message
        if response.status().as_u16() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(|e| RegistryError::Error(format!("Failed to parse error response {e}")))?;

            return Err(RegistryError::Forbidden(error.error));
        }

        let updated = response.json::<UpdateCardResponse>().map_err(|e| {
            RegistryError::Error(format!("Failed to parse update card response {e}"))
        })?;

        if updated.updated {
            Ok(())
        } else {
            Err(RegistryError::Error("Failed to update card".to_string()))
        }
    }

    pub fn delete_card(&self, delete_request: DeleteCardRequest) -> Result<(), RegistryError> {
        let query_string = serde_qs::to_string(&delete_request)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {e}")))?;

        let response = self
            .api_client
            .request(
                Routes::CardDelete,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .map_err(|e| {
                error!("Request failed {}", e);
                e
            })?;

        // check if 403 forbidden and get error message
        if response.status().as_u16() == 403 {
            let error = response
                .json::<ErrorResponse>()
                .map_err(|e| RegistryError::Error(format!("Failed to parse error response {e}")))?;

            return Err(RegistryError::Forbidden(error.error));
        }

        let deleted = response
            .json::<UidResponse>()
            .map_err(|e| RegistryError::Error(format!("Failed to parse uid response {e}")))?;

        if !deleted.exists {
            Ok(())
        } else {
            Err(RegistryError::Error("Failed to delete card".to_string()))
        }
    }

    #[instrument(skip_all)]
    pub fn load_card(&self, args: CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        let query_string = serde_qs::to_string(&args)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request(
                Routes::CardLoad,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .map_err(|e| RegistryError::Error(format!("Failed to load_card {}", e)))?;

        response.json::<ArtifactKey>().map_err(|e| {
            RegistryError::Error(format!("Failed to parse artifact key response {}", e))
        })
    }

    pub fn check_uid_exists(&self, uid: &str) -> Result<bool, RegistryError> {
        let uid_request = UidRequest {
            uid: uid.to_string(),
            registry_type: self.registry_type.clone(),
        };
        let query_string = serde_qs::to_string(&uid_request)
            .map_err(|e| RegistryError::Error(format!("Failed to serialize query args {}", e)))?;

        let response = self
            .api_client
            .request(
                Routes::Card,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .map_err(|e| RegistryError::Error(format!("Failed to check uid exists {}", e)))?;

        let exists = response
            .json::<UidResponse>()
            .map_err(|e| RegistryError::Error(format!("Failed to parse uid response {}", e)))?;

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

        let query_string = serde_qs::to_string(&key_request).map_err(|e| {
            error!("Failed to serialize query args {}", e);
            RegistryError::Error(format!("Failed to serialize query args {}", e))
        })?;

        let response = self
            .api_client
            .request(route, RequestType::Get, None, Some(query_string), None)
            .map_err(|e| {
                error!("Failed to get artifact key {}", e);
                RegistryError::Error(format!("Failed to get artifact key {}", e))
            })?;

        let key = response.json::<ArtifactKey>().map_err(|e| {
            error!("Failed to parse artifact key {}", e);
            RegistryError::Error(format!("Failed to parse artifact key {}", e))
        })?;

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
        let body = serde_json::to_value(metrics).map_err(|e| {
            error!("Failed to serialize metrics {}", e);
            RegistryError::Error(format!("Failed to serialize metrics {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to insert hardware metrics {}", e);
                RegistryError::Error(format!("Failed to insert hardware metrics {}", e))
            })?;

        let inserted = response.json::<HardwareMetricResponse>().map_err(|e| {
            error!("Failed to parse hardware metric response {}", e);
            RegistryError::Error(format!("Failed to parse hardware metric response {}", e))
        })?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::Error(
                "Failed to insert hardware metrics".to_string(),
            ))
        }
    }

    pub fn get_hardware_metrics(
        &self,
        metrics: &GetHardwareMetricRequest,
    ) -> Result<Vec<HardwareMetrics>, RegistryError> {
        let query_string = serde_qs::to_string(metrics).map_err(|e| {
            error!("Failed to serialize metrics {}", e);
            RegistryError::Error(format!("Failed to serialize metrics {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentHardwareMetrics,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .map_err(|e| {
                error!("Failed to get hardware metrics {}", e);
                RegistryError::Error(format!("Failed to get hardware metrics {}", e))
            })?;

        response.json::<Vec<HardwareMetrics>>().map_err(|e| {
            RegistryError::Error(format!("Failed to parse hardware metric response {}", e))
        })
    }

    pub fn insert_metrics(&self, metrics: &MetricRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(metrics).map_err(|e| {
            error!("Failed to serialize metrics {}", e);
            RegistryError::Error(format!("Failed to serialize metrics {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentMetrics,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to insert metrics {}", e);
                RegistryError::Error(format!("Failed to insert metrics {}", e))
            })?;

        let inserted = response.json::<MetricResponse>().map_err(|e| {
            error!("Failed to parse metric response {}", e);
            RegistryError::Error(format!("Failed to parse metric response {}", e))
        })?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::Error("Failed to insert metrics".to_string()))
        }
    }

    pub fn get_metrics(&self, metrics: &GetMetricRequest) -> Result<Vec<Metric>, RegistryError> {
        let body = serde_json::to_value(metrics).map_err(|e| {
            error!("Failed to serialize metrics {}", e);
            RegistryError::Error(format!("Failed to serialize metrics {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentMetrics,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to get metrics {}", e);
                RegistryError::Error(format!("Failed to get metrics {}", e))
            })?;

        response
            .json::<Vec<Metric>>()
            .map_err(|e| RegistryError::Error(format!("Failed to parse metric response {}", e)))
    }

    pub fn insert_parameters(&self, parameters: &ParameterRequest) -> Result<(), RegistryError> {
        let body = serde_json::to_value(parameters).map_err(|e| {
            error!("Failed to serialize parameters {}", e);
            RegistryError::Error(format!("Failed to serialize parameters {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentParameters,
                RequestType::Put,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to insert parameters {}", e);
                RegistryError::Error(format!("Failed to insert parameters {}", e))
            })?;

        let inserted = response.json::<ParameterResponse>().map_err(|e| {
            error!("Failed to parse parameter response {}", e);
            RegistryError::Error(format!("Failed to parse parameter response {}", e))
        })?;

        if inserted.success {
            Ok(())
        } else {
            Err(RegistryError::Error(
                "Failed to insert parameters".to_string(),
            ))
        }
    }

    pub fn get_parameters(
        &self,
        parameters: &GetParameterRequest,
    ) -> Result<Vec<Parameter>, RegistryError> {
        let body = serde_json::to_value(parameters).map_err(|e| {
            error!("Failed to serialize parameters {}", e);
            RegistryError::Error(format!("Failed to serialize parameters {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ExperimentParameters,
                RequestType::Post,
                Some(body),
                None,
                None,
            )
            .map_err(|e| {
                error!("Failed to get parameters {}", e);
                RegistryError::Error(format!("Failed to get parameters {}", e))
            })?;

        response
            .json::<Vec<Parameter>>()
            .map_err(|e| RegistryError::Error(format!("Failed to parse parameter response {}", e)))
    }
}
