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
