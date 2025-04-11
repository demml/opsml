use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use opsml_settings::OpsmlMode;
use opsml_toml::{OpsmlTools, PyProjectToml};
use std::path::Path;
use std::sync::Arc;
use std::sync::OnceLock;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tracing::{debug, error};

//    pub api_client: Arc<OpsmlApiClient>,

pub struct OpsmlState {
    pub config: RwLock<OpsmlConfig>,
    pub runtime: Arc<Runtime>,
    pub tools: RwLock<Option<OpsmlTools>>,
    pub mode: RwLock<OpsmlMode>,
}

impl OpsmlState {
    fn new() -> Result<Self, StateError> {
        let config = OpsmlConfig::new();

        let runtime = Arc::new(Runtime::new().map_err(|e| {
            error!("Failed to create runtime: {}", e);
            StateError::Error(format!("Failed to create runtime with error: {}", e))
        })?);
        // Initialize tools from pyproject.toml

        let tools = Self::load_tools(&config.base_path)?;
        let mode = config.mode.clone();

        Ok(Self {
            config: RwLock::new(config),
            runtime,
            tools: RwLock::new(tools),
            mode: RwLock::new(mode),
        })
    }

    pub fn load_tools(path: &Path) -> Result<Option<OpsmlTools>, StateError> {
        let tools = match PyProjectToml::load(Some(path), None) {
            Ok(toml) => toml.get_tools(),
            Err(e) => {
                debug!("Failed to load pyproject.toml, defaulting to None: {}", e);
                None
            }
        };

        Ok(tools)
    }

    pub fn tools(&self) -> Result<std::sync::RwLockReadGuard<'_, Option<OpsmlTools>>, StateError> {
        self.tools
            .read()
            .map_err(|e| StateError::Error(format!("Failed to read tools: {}", e)))
    }

    pub fn config(&self) -> Result<std::sync::RwLockReadGuard<'_, OpsmlConfig>, StateError> {
        self.config
            .read()
            .map_err(|e| StateError::Error(format!("Failed to read config: {}", e)))
    }

    pub fn mode(&self) -> Result<std::sync::RwLockReadGuard<'_, OpsmlMode>, StateError> {
        self.mode
            .read()
            .map_err(|e| StateError::Error(format!("Failed to read mode: {}", e)))
    }

    pub fn reset_mode(&self) -> Result<(), StateError> {
        let new_mode = {
            let config = self.config()?;
            config.mode.clone()
        };
        let mut mode = self
            .mode
            .write()
            .map_err(|e| StateError::Error(format!("Failed to write mode: {}", e)))?;
        *mode = new_mode;
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

    pub fn reset_tools(&self) -> Result<(), StateError> {
        let config = self.config()?;
        let tools = Self::load_tools(&config.base_path)?;
        let mut tools_lock = self
            .tools
            .write()
            .map_err(|e| StateError::Error(format!("Failed to write tools: {}", e)))?;
        *tools_lock = tools;
        debug!("Tools reset to: {:?}", tools_lock);
        Ok(())
    }

    pub fn reset_app_state(&self) -> Result<(), StateError> {
        self.reset_config()?;
        self.reset_mode()?;
        self.reset_tools()?;

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
