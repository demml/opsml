use crate::error::RegistryError;
use crate::registries::client::base::Registry;
use opsml_client::error::ApiClientError;
use opsml_client::OpsmlApiClient;
use opsml_types::{api::*, cards::CardTable, contracts::*, RegistryType};
use std::sync::Arc;
use tracing::error;

#[derive(Debug, Clone)]
pub struct ClientArtifactRegistry {
    registry_type: RegistryType,
    pub api_client: Arc<OpsmlApiClient>,
}

impl ClientArtifactRegistry {
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

impl Registry for ClientArtifactRegistry {
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

pub trait ArtifactRegistry: Registry {
    /// Insert an artifact record into the opsml_artifact_registry
    /// # Arguments
    /// * `space` - The space of the artifact
    /// * `name` - The name of the artifact
    /// * `version` - The version of the artifact
    /// * `filename` - The filename of the artifact
    /// * `media_type` - The media type of the artifact
    /// # Returns
    /// * `CreateArtifactResponse` - The response containing the created artifact record
    fn log_artifact(
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
            .client()
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

    fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, RegistryError> {
        // Query artifacts from the registry
        let params = serde_qs::to_string(query_args)?;

        let response = self
            .client()
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

// this is used in a few place
pub trait ArtifactExt: Registry {
    fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        let key_request = ArtifactKeyRequest {
            uid: uid.to_string(),
            registry_type: registry_type.clone(),
        };

        let query_string = serde_qs::to_string(&key_request)?;

        let response = self
            .client()
            .request(
                Routes::ArtifactKey,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get artifact key {}", e);
            })?;

        let key = response
            .json::<ArtifactKey>()
            .map_err(RegistryError::RequestError)?;

        Ok(key)
    }
}
