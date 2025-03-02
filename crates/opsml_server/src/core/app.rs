use crate::core::router::create_router;
use crate::core::setup::setup_components;
use crate::core::state::AppState;
use anyhow::Ok;
use anyhow::Result;
use axum::Router;
use opsml_auth::auth::AuthManager;
use std::sync::Arc;
use tracing::{info, warn};

pub async fn create_app() -> Result<Router> {
    // setup components (config, logging, storage client)
    let (config, storage_client, sql_client) = setup_components().await?;
    let storage_settings = config.storage_settings()?;

    // Create shared state for the application (storage client, auth manager, config)
    let app_state = Arc::new(AppState {
        storage_client: Arc::new(storage_client),
        sql_client: Arc::new(sql_client),
        auth_manager: Arc::new(AuthManager::new(
            &config.auth_settings.jwt_secret,
            &config.auth_settings.refresh_secret,
        )),
        config: Arc::new(config),
        storage_settings: Arc::new(storage_settings),
    });

    info!("✅ Application state created");

    // create the router
    let app = create_router(app_state).await?;

    info!("✅ Router created");

    Ok(app)
}
