use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use opsml_settings::OpsmlMode;
use std::sync::Arc;
use std::sync::OnceLock;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tracing::error;

//    pub api_client: Arc<OpsmlApiClient>,

pub struct OpsmlState {
    pub config: RwLock<OpsmlConfig>,
    pub runtime: Arc<Runtime>,
}

impl OpsmlState {
    fn new() -> Result<Self, StateError> {
        let config = RwLock::new(OpsmlConfig::new());

        let runtime = Arc::new(Runtime::new().map_err(|e| {
            error!("Failed to create runtime: {}", e);
            StateError::Error(format!("Failed to create runtime with error: {}", e))
        })?);

        Ok(Self { config, runtime })
    }

    pub fn config(&self) -> Result<OpsmlConfig, StateError> {
        self.config
            .read()
            .map_err(|e| StateError::Error(format!("Failed to read config: {}", e)))
            .map(|config| config.clone())
    }

    pub fn mode(&self) -> Result<OpsmlMode, StateError> {
        self.config
            .read()
            .map_err(|e| StateError::Error(format!("Failed to read config: {}", e)))
            .map(|config| config.mode.clone())
    }

    pub fn update_config<F>(&self, f: F) -> Result<(), StateError>
    where
        F: FnOnce(&mut OpsmlConfig),
    {
        let mut config = self
            .config
            .write()
            .map_err(|e| StateError::Error(format!("Failed to write config: {}", e)))?;
        f(&mut config);
        Ok(())
    }

    pub fn reset_config(&self) -> Result<(), StateError> {
        let mut config = self
            .config
            .write()
            .map_err(|e| StateError::Error(format!("Failed to write config: {}", e)))?;
        *config = OpsmlConfig::new();
        Ok(())
    }

    pub fn start_runtime(&self) -> Arc<Runtime> {
        self.runtime.clone()
    }

    pub fn block_on<F, T>(&self, future: F) -> T
    where
        F: std::future::Future<Output = T>,
    {
        self.runtime.block_on(future)
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

static API_CLIENT: OnceLock<Arc<OpsmlApiClient>> = OnceLock::new();

pub fn get_api_client() -> &'static Arc<OpsmlApiClient> {
    API_CLIENT.get_or_init(|| {
        let state = app_state();
        let config = state.config().unwrap();

        let settings = config
            .storage_settings()
            .map_err(|e| {
                error!("Failed to get storage settings: {}", e);
                StateError::Error(format!("Failed to get storage settings with error: {}", e))
            })
            .expect("Failed to get storage settings");

        // Initialize API client
        let api_client = build_api_client(&settings)
            .map_err(|e| {
                error!("Failed to create api client: {}", e);
                StateError::Error(format!("Failed to create api client with error: {}", e))
            })
            .expect("Failed to create api client");

        Arc::new(api_client)
    })
}
