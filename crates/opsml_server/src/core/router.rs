use crate::core::auth::middleware::auth_api_middleware;
use crate::core::auth::route::get_auth_router;
use crate::core::cards::route::get_card_router;
use crate::core::debug::route::get_debug_router;
use crate::core::files::route::get_file_router;
use crate::core::health::route::get_health_router;
use crate::core::run::route::get_run_router;
use crate::core::settings::route::get_settings_router;
use crate::core::state::AppState;
use anyhow::Result;
use axum::http::{
    header::{ACCEPT, AUTHORIZATION, CONTENT_TYPE},
    Method,
};
use axum::{middleware, Router};
use std::sync::Arc;
use tower_http::cors::CorsLayer;

const ROUTE_PREFIX: &str = "/opsml";

pub async fn create_router(app_state: Arc<AppState>) -> Result<Router> {
    let cors = CorsLayer::new()
        .allow_methods([
            Method::GET,
            Method::PUT,
            Method::DELETE,
            Method::POST,
            Method::PATCH,
        ])
        .allow_credentials(true)
        .allow_headers([AUTHORIZATION, ACCEPT, CONTENT_TYPE]);

    let debug_routes = get_debug_router(ROUTE_PREFIX).await?;
    let health_routes = get_health_router(ROUTE_PREFIX).await?;
    let file_routes = get_file_router(ROUTE_PREFIX).await?;
    let settings_routes = get_settings_router(ROUTE_PREFIX).await?;
    let card_routes = get_card_router(ROUTE_PREFIX).await?;
    let run_routes = get_run_router(ROUTE_PREFIX).await?;
    let auth_routes = get_auth_router(ROUTE_PREFIX).await?;

    // merge all the routes except the auth routes
    // All routes except the auth routes will be protected by the auth middleware
    let merged_routes = Router::new()
        .merge(debug_routes)
        .merge(health_routes)
        .merge(settings_routes)
        .merge(file_routes)
        .merge(card_routes)
        .merge(run_routes)
        .route_layer(middleware::from_fn_with_state(
            app_state.clone(),
            auth_api_middleware,
        ));

    Ok(Router::new()
        .merge(merged_routes)
        .merge(auth_routes)
        .layer(cors)
        .with_state(app_state))
}
