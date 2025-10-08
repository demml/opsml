use crate::core::error::ServerError;
use crate::core::middleware::connection::ConnectionTracker;
use crate::core::scouter::client::ScouterApiClient;
use opsml_auth::auth::AuthManager;
use opsml_auth::permission::UserPermissions;
use opsml_events::EventBus;
use opsml_settings::config::{OpsmlConfig, OpsmlStorageSettings};
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::traits::UserLogicTrait;
use opsml_storage::storage::enums::client::StorageClientEnum;
use std::sync::Arc;
use tracing::error;

pub struct AppState {
    pub storage_client: Arc<StorageClientEnum>,
    pub sql_client: Arc<SqlClientEnum>,
    pub auth_manager: AuthManager,
    pub config: OpsmlConfig,
    pub storage_settings: OpsmlStorageSettings,
    pub scouter_client: ScouterApiClient,
    pub event_bus: EventBus,
    pub connection_tracker: Option<Arc<ConnectionTracker>>,
}

impl AppState {
    pub async fn exchange_token_from_perms(
        &self,
        perms: &UserPermissions,
    ) -> Result<String, ServerError> {
        let user = self
            .sql_client
            .get_user(&perms.username, None)
            .await?
            .ok_or_else(|| {
                error!("User not found in database");
                ServerError::UserNotFoundError
            })?;

        self.auth_manager
            .exchange_token_for_scouter(&user)
            .await
            .map_err(|e| {
                error!("Failed to exchange token from permissions: {e}");
                e.into()
            })
    }
}
