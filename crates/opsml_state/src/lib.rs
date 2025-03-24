use futures::future::FutureExt;
use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use std::sync::Arc;
use std::sync::OnceLock;
use tracing::error;

pub struct OpsmlState {
    pub config: OpsmlConfig,
    pub api_client: Arc<OpsmlApiClient>,
}

impl OpsmlState {
    async fn new() -> Result<Self, StateError> {
        let config = OpsmlConfig::new();

        let settings = config.storage_settings().map_err(|e| {
            error!("Failed to get storage settings: {}", e);
            StateError::Error(format!("Failed to get storage settings with error: {}", e))
        })?;

        // Initialize API client
        let api_client = build_api_client(&settings).await.map_err(|e| {
            error!("Failed to create api client: {}", e);
            StateError::Error(format!("Failed to create api client with error: {}", e))
        })?;

        let api_client = Arc::new(api_client);

        Ok(Self { config, api_client })
    }

    pub fn api_client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }

    pub fn config(&self) -> &OpsmlConfig {
        &self.config
    }
}

// Global instance
static INSTANCE: OnceLock<Arc<OpsmlState>> = OnceLock::new();

// Global accessor
pub async fn get_state() -> &'static Arc<OpsmlState> {
    INSTANCE.get_or_init(|| {
        async move {
            let state = OpsmlState::new().await;
            Arc::new(state)
        }
        .now_or_never()
        .expect("Failed to initialize OpsmlState")
    })
}
