// The async module provides a standalone async Opsml registry
// This is currently used as part of the ServiceReloader struct.
// Having the async registry separate allows for easier reuse and less overhead,
// as we don't want to require every call to the main OpsML registry to
// instantiate an async client.

use crate::error::RegistryError;
use opsml_client::OpsmlApiAsyncClient;
use opsml_settings::OpsmlMode;
use opsml_state::{app_state, get_async_api_client};
use opsml_types::contracts::{ArtifactKey, CardQueryArgs, CardRecord};
use opsml_types::{RegistryType, RequestType, Routes};
use std::sync::Arc;
use tracing::{debug, error, info, instrument};

#[derive(Debug, Clone)]
pub struct AsyncOpsmlRegistry {
    registry_type: RegistryType,
    api_client: Arc<OpsmlApiAsyncClient>,
}

impl AsyncOpsmlRegistry {
    pub async fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let state = &app_state();
        let api_client = get_async_api_client().await.clone();
        let mode = &*state.mode()?;

        // Async registry is only supported in client context
        match mode {
            OpsmlMode::Server => {
                error!("AsyncOpsmlRegistry only supports client mode");
                return Err(RegistryError::AsyncOpsmlRegistryOnlySupportsClientMode);
            }
            OpsmlMode::Client => {
                debug!("Running in client mode");
            }
        }

        Ok(Self {
            api_client,
            registry_type,
        })
    }

    #[instrument(skip_all)]
    pub async fn list_cards_async(
        &self,
        args: &CardQueryArgs,
    ) -> Result<Vec<CardRecord>, RegistryError> {
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
            .await
            .inspect_err(|e| {
                error!("Failed to list cards {}", e);
            })?;

        response
            .json::<Vec<CardRecord>>()
            .await
            .map_err(RegistryError::RequestError)
    }

    #[instrument(skip_all)]
    pub async fn get_key(&self, args: &CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
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
            .await
            .inspect_err(|e| {
                error!("Failed to get artifact key {}", e);
            })?;

        response
            .json::<ArtifactKey>()
            .await
            .map_err(RegistryError::RequestError)
    }
}
