use futures::FutureExt;
use opsml_client::client::{build_api_client, OpsmlApiClient};
use opsml_settings::OpsmlConfig;
use std::sync::Arc;
use std::sync::OnceLock;
use tokio::sync::Mutex;

static API_CLIENT: OnceLock<Arc<OpsmlApiClient>> = OnceLock::new();

pub fn get_api_client() -> &'static Arc<OpsmlApiClient> {
    API_CLIENT.get_or_init(|| {
        async move {
            let config = OpsmlConfig::new(None);
            let settings = config.storage_settings().unwrap();
            let client = build_api_client(&settings)
                .await
                .map_err(|e| {
                    error!("Failed to create api client: {}", e);
                    ApiError::Error(format!("Failed to create api client with error: {}", e))
                })
                .unwrap();

            Arc::new(client)
        }
        .now_or_never()
        .expect("Failed to initialize api client")
    })
}

/// Get the storage client instance
pub async fn get_storage() -> &'static Arc<Mutex<FileSystemStorage>> {
    STORAGE.get_or_init(|| {
        async move {
            let config = OpsmlConfig::default();
            let mut settings = config.storage_settings().unwrap();
            let api_client = get_api_client();
            let storage = FileSystemStorage::new(&mut settings, api_client)
                .await
                .expect("Failed to create file system storage");

            Arc::new(Mutex::new(storage))
        }
        .now_or_never()
        .expect("Failed to initialize storage")
    })
}

pub fn get_opsml_mode() -> &'static OpsmlMode {
    OPSML_MODE.get_or_init(|| {
        OpsmlConfig::default();

        if OpsmlConfig::is_using_client(&env::var("OPSML_TRACKING_URI").unwrap_or_default()) {
            OpsmlMode::Client
        } else {
            OpsmlMode::Server
        }
    })
}
