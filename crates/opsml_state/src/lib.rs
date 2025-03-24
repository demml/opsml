use futures::FutureExt;
use opsml_client::base::{build_api_client, OpsmlApiClient};
use opsml_error::error::StateError;
use opsml_settings::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use std::sync::Arc;
use std::sync::OnceLock;
use tokio::sync::Mutex;

pub struct OpsmlState {
    api_client: Arc<OpsmlApiClient>,
    storage: Arc<FileSystemStorage>,
    mode: OpsmlMode,
}

impl OpsmlState {
    async fn new() -> Result<Self, StateError> {
        let config = OpsmlConfig::new(None);
        let settings = config.storage_settings().unwrap();

        // Initialize API client
        let api_client = build_api_client(&settings).await.map_err(|e| {
            error!("Failed to create api client: {}", e);
            StateError::Error(format!("Failed to create api client with error: {}", e))
        })?;

        let api_client = Arc::new(api_client);

        // Initialize storage
        let mut settings = config.storage_settings().map_err(|e| {
            error!("Failed to get storage settings: {}", e);
            StateError::Error(format!("Failed to get storage settings with error: {}", e))
        })?;

        let storage = FileSystemStorage::new(&mut settings, &api_client)
            .await
            .expect("Failed to create file system storage");
        let storage = Arc::new(Mutex::new(storage));

        // Initialize mode
        let mode =
            if OpsmlConfig::is_using_client(&env::var("OPSML_TRACKING_URI").unwrap_or_default()) {
                OpsmlMode::Client
            } else {
                OpsmlMode::Server
            };

        Self {
            api_client,
            storage,
            mode,
        }
    }

    pub fn api_client(&self) -> &Arc<OpsmlApiClient> {
        &self.api_client
    }

    pub fn storage(&self) -> &Arc<Mutex<FileSystemStorage>> {
        &self.storage
    }

    pub fn mode(&self) -> &OpsmlMode {
        &self.mode
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
