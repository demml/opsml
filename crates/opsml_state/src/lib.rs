use futures::future::FutureExt;
use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use opsml_settings::OpsmlMode;
use std::sync::Arc;
use std::sync::OnceLock;
use tokio::runtime::Runtime;
use tracing::error;

pub struct OpsmlState {
    pub config: OpsmlConfig,
    pub api_client: Arc<OpsmlApiClient>,
    pub runtime: Arc<tokio::runtime::Runtime>,
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
        let runtime = Runtime::new().map_err(|e| {
            error!("Failed to create runtime: {}", e);
            StateError::Error(format!("Failed to create runtime with error: {}", e))
        })?;

        Ok(Self {
            config,
            api_client,
            runtime: Arc::new(runtime),
        })
    }

    pub fn api_client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }

    pub fn config(&self) -> &OpsmlConfig {
        &self.config
    }

    pub fn runtime(&self) -> &Arc<tokio::runtime::Runtime> {
        &self.runtime
    }

    pub fn mode(&self) -> &OpsmlMode {
        &self.config.mode
    }
}

// Global instance
static INSTANCE: OnceLock<Arc<OpsmlState>> = OnceLock::new();

// Global accessor
pub fn get_state() -> &'static Arc<OpsmlState> {
    INSTANCE.get_or_init(|| {
        async move {
            let state = OpsmlState::new()
                .await
                .map_err(|e| {
                    error!("Failed to get state: {}", e);
                    StateError::Error(format!("Failed to get state with error: {}", e))
                })
                .unwrap();
            Arc::new(state)
        }
        .now_or_never()
        .expect("Failed to get state")
    })
}
