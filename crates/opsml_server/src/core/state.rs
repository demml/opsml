use opsml_auth::auth::AuthManager;
use opsml_settings::config::OpsmlConfig;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_storage::storage::enums::client::StorageClientEnum;
use std::sync::Arc;

pub struct AppState {
    pub storage_client: Arc<StorageClientEnum>,
    pub sql_client: Arc<SqlClientEnum>,
    pub auth_manager: Arc<AuthManager>,
    pub config: Arc<OpsmlConfig>,
}
