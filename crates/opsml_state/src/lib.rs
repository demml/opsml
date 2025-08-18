pub mod error;
pub use error::StateError;
use opsml_client::base::{
    build_api_client, build_async_api_client, OpsmlApiAsyncClient, OpsmlApiClient,
};
use opsml_settings::OpsmlConfig;
use opsml_settings::OpsmlMode;
use opsml_toml::{OpsmlTools, PyProjectToml};
use std::path::Path;
use std::sync::Arc;
use std::sync::OnceLock;
use std::sync::RwLock;
use tokio::runtime::Runtime;
use tracing::debug;

pub struct OpsmlState {
    pub config: RwLock<OpsmlConfig>,
    pub runtime: Arc<Runtime>,
    pub tools: RwLock<Option<OpsmlTools>>,
    pub mode: RwLock<OpsmlMode>,
}

impl OpsmlState {
    fn new() -> Result<Self, StateError> {
        let config = OpsmlConfig::new();

        let runtime = Arc::new(Runtime::new().map_err(StateError::RuntimeError)?);
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
                debug!("Failed to load pyproject.toml, defaulting to None: {e}");
                None
            }
        };

        Ok(tools)
    }

    pub fn tools(&self) -> Result<std::sync::RwLockReadGuard<'_, Option<OpsmlTools>>, StateError> {
        self.tools
            .read()
            .map_err(|e| StateError::ReadToolsError(e.to_string()))
    }

    pub fn config(&self) -> Result<std::sync::RwLockReadGuard<'_, OpsmlConfig>, StateError> {
        self.config
            .read()
            .map_err(|e| StateError::ReadConfigError(e.to_string()))
    }

    pub fn mode(&self) -> Result<std::sync::RwLockReadGuard<'_, OpsmlMode>, StateError> {
        self.mode
            .read()
            .map_err(|e| StateError::ReadModeError(e.to_string()))
    }

    pub fn reset_mode(&self) -> Result<(), StateError> {
        let new_mode = {
            let config = self.config()?;
            config.mode.clone()
        };
        let mut mode = self
            .mode
            .write()
            .map_err(|e| StateError::ReadModeError(e.to_string()))?;
        *mode = new_mode;
        Ok(())
    }

    pub fn reset_config(&self) -> Result<(), StateError> {
        let mut config = self
            .config
            .write()
            .map_err(|e| StateError::WriteConfigError(e.to_string()))?;

        *config = OpsmlConfig::new();
        Ok(())
    }

    pub fn reset_tools(&self) -> Result<(), StateError> {
        let config = self.config()?;
        let tools = Self::load_tools(&config.base_path)?;
        let mut tools_lock = self
            .tools
            .write()
            .map_err(|e| StateError::WriteToolsError(e.to_string()))?;
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
    INSTANCE.get_or_init(|| OpsmlState::new().expect("Failed to initialize state"))
}

static API_CLIENT: OnceLock<Arc<OpsmlApiClient>> = OnceLock::new();
static ASYNC_API_CLIENT: OnceLock<Arc<OpsmlApiAsyncClient>> = OnceLock::new();

pub fn get_api_client() -> &'static Arc<OpsmlApiClient> {
    API_CLIENT.get_or_init(|| {
        let state = app_state();
        let config = state.config().unwrap();

        let settings = config
            .storage_settings()
            .expect("Failed to get storage settings");

        // Initialize API client
        let api_client = build_api_client(&settings).expect("Failed to create api client");

        Arc::new(api_client)
    })
}

fn build_async_client() -> Arc<OpsmlApiAsyncClient> {
    let state = app_state();
    let config = state.config().unwrap();

    let settings = config
        .storage_settings()
        .expect("Failed to get storage settings");

    // Initialize async API client - need an async block here
    let api_client = state
        .block_on(async { build_async_api_client(&settings).await })
        .expect("Failed to create asyc api client");

    Arc::new(api_client)
}

pub fn get_async_api_client() -> &'static Arc<OpsmlApiAsyncClient> {
    ASYNC_API_CLIENT.get_or_init(build_async_client)
}
