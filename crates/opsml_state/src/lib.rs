use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use opsml_settings::OpsmlMode;
use std::sync::Arc;
use std::sync::OnceLock;
use tokio::runtime::Runtime;
use tokio::sync::OnceCell;
use tracing::error;

//    pub api_client: Arc<OpsmlApiClient>,

pub struct OpsmlState {
    pub config: OpsmlConfig,
    pub runtime: Arc<Runtime>,
}

impl OpsmlState {
    fn new() -> Result<Self, StateError> {
        let config = OpsmlConfig::new();

        let runtime = Arc::new(Runtime::new().map_err(|e| {
            error!("Failed to create runtime: {}", e);
            StateError::Error(format!("Failed to create runtime with error: {}", e))
        })?);

        Ok(Self { config, runtime })
    }

    pub fn config(&self) -> &OpsmlConfig {
        &self.config
    }

    pub fn mode(&self) -> &OpsmlMode {
        &self.config.mode
    }

    pub fn start_runtime(&self) -> Arc<Runtime> {
        self.runtime.clone()
    }
}

// Global instance
static INSTANCE: OnceLock<OpsmlState> = OnceLock::new();

// Global accessor
// Then modify your app_state() to use this runtime
pub fn app_state() -> &'static OpsmlState {
    INSTANCE.get_or_init(|| {
        OpsmlState::new()
            .map_err(|e| {
                error!("Failed to get state: {}", e);
                StateError::Error(format!("Failed to get state with error: {}", e))
            })
            .expect("Failed to initialize state")
    })
}

static API_CLIENT: OnceCell<Arc<OpsmlApiClient>> = OnceCell::const_new();

pub async fn get_api_client() -> Arc<OpsmlApiClient> {
    API_CLIENT
        .get_or_init(|| async {
            let state = app_state();
            let config = state.config();

            let settings = config
                .storage_settings()
                .map_err(|e| {
                    error!("Failed to get storage settings: {}", e);
                    StateError::Error(format!("Failed to get storage settings with error: {}", e))
                })
                .expect("Failed to get storage settings");

            // Initialize API client
            let api_client = build_api_client(&settings)
                .await
                .map_err(|e| {
                    error!("Failed to create api client: {}", e);
                    StateError::Error(format!("Failed to create api client with error: {}", e))
                })
                .expect("Failed to create api client");

            Arc::new(api_client)
        })
        .await
        .clone()
}
