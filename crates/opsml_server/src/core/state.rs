use crate::core::scouter::client::ScouterApiClient;
use opsml_auth::auth::AuthManager;
use opsml_auth::permission::UserPermissions;
use opsml_error::ApiError;
use opsml_events::EventBus;
use opsml_settings::config::{OpsmlConfig, OpsmlStorageSettings};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_storage::storage::enums::client::StorageClientEnum;
use std::sync::Arc;
use tracing::error;

pub struct AppState {
    pub storage_client: Arc<StorageClientEnum>,
    pub sql_client: Arc<SqlClientEnum>,
    pub auth_manager: Arc<AuthManager>,
    pub config: Arc<OpsmlConfig>,
    pub storage_settings: Arc<OpsmlStorageSettings>,
    pub scouter_client: Arc<ScouterApiClient>,
    pub event_bus: EventBus,
}

impl AppState {
    pub async fn exchange_token_from_perms(
        &self,
        perms: &UserPermissions,
    ) -> Result<String, ApiError> {
        let user = self
            .sql_client
            .get_user(&perms.username)
            .await
            .map_err(|e| {
                error!("Failed to get user from database: {}", e);
                ApiError::Error("Failed to get user from database".to_string())
            })?
            .ok_or_else(|| {
                error!("User not found in database");
                ApiError::Error("User not found in database".to_string())
            })?;

        self.auth_manager
            .exchange_token_for_scouter(&user)
            .await
            .map_err(|e| {
                error!("Failed to exchange token from permissions: {}", e);
                ApiError::Error("Failed to exchange token from permissions".to_string())
            })
    }
}
