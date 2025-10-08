use crate::core::audit::AuditEventHandler;
use crate::core::middleware::connection::ConnectionTracker;
use crate::core::router::create_router;
use crate::core::setup::{initialize_default_user, setup_components};
use crate::core::state::AppState;
use anyhow::Ok;
use anyhow::Result;
use axum::Router;
use opsml_auth::auth::AuthManager;
use opsml_events::EventBus;
use std::sync::Arc;
use tracing::{info, warn};

pub async fn create_app() -> Result<Router> {
    // setup components (config, logging, storage client)
    let (config, storage_client, sql_client, scouter_client) = setup_components().await?;
    let storage_settings = config.storage_settings()?;

    // Setup basic auth and sso
    let auth_manager = AuthManager::new(
        &config.auth_settings.jwt_secret,
        &config.auth_settings.refresh_secret,
        &config.auth_settings.scouter_secret,
    )
    .await?;

    let connection_tracker = if config.track_connections {
        Some(Arc::new(ConnectionTracker::new()))
    } else {
        None
    };

    // Create shared state for the application (storage client, auth manager, config)
    let app_state = Arc::new(AppState {
        storage_client: Arc::new(storage_client),
        sql_client: Arc::new(sql_client),
        auth_manager,
        config,
        storage_settings,
        scouter_client,
        event_bus: EventBus::new(100),
        connection_tracker,
    });

    // Initialize the event bus
    let event_handler = AuditEventHandler::new(app_state.clone());
    event_handler.start().await;

    // Initialize default user if none exists
    if let Err(e) = initialize_default_user(&app_state.sql_client, &app_state.scouter_client).await
    {
        // Log error but don't fail startup
        warn!("Failed to initialize default user: {e}");
    }

    info!("✅ Application state created");

    // create the router
    let app = create_router(app_state).await?;

    info!("✅ Router created");

    Ok(app)
}
