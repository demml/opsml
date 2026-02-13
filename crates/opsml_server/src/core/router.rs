use crate::core::auth::middleware::auth_api_middleware;
use crate::core::auth::route::get_auth_router;
use crate::core::cards::route::get_card_router;
use crate::core::debug::route::get_debug_router;
use crate::core::experiment::route::get_experiment_router;
use crate::core::files::route::get_file_router;
use crate::core::genai::route::get_genai_router;
use crate::core::health::route::get_health_router;
use crate::core::middleware::event::event_middleware;
use crate::core::middleware::metrics::track_metrics;
use crate::core::scouter::route::get_scouter_router;
use crate::core::settings::route::get_settings_router;
use crate::core::state::AppState;
use crate::core::user::route::get_user_router;
use anyhow::Result;
use axum::http::{
    Method,
    header::{ACCEPT, AUTHORIZATION, CONTENT_TYPE},
};
use axum::{Router, middleware};
use reqwest::header::HeaderValue;
use std::sync::Arc;
use tower_http::cors::CorsLayer;

const ROUTE_PREFIX: &str = "/opsml/api";

pub async fn create_router(app_state: Arc<AppState>) -> Result<Router> {
    let cors = CorsLayer::new()
        .allow_origin("http://localhost:3000".parse::<HeaderValue>()?)
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
    let run_routes = get_experiment_router(ROUTE_PREFIX).await?;
    let auth_routes = get_auth_router(ROUTE_PREFIX).await?;
    let user_routes = get_user_router(ROUTE_PREFIX).await?;
    let scouter_routes = get_scouter_router(ROUTE_PREFIX).await?;
    let genai_routes = get_genai_router(ROUTE_PREFIX).await?;

    // merge all the routes except the auth routes
    // All routes except the auth, healthcheck, ui and ui settings routes are protect by the auth middleware
    let merged_routes = Router::new()
        .merge(debug_routes)
        .merge(file_routes)
        .merge(card_routes)
        .merge(run_routes)
        .merge(user_routes)
        .merge(scouter_routes)
        .merge(genai_routes)
        .route_layer(middleware::from_fn_with_state(
            // Audit middleware occurs last.
            //Audit middleware passes the request to the request handler
            app_state.clone(),
            event_middleware,
        ))
        .route_layer(middleware::from_fn_with_state(
            // Auth middleware occurs first
            app_state.clone(),
            auth_api_middleware,
        ));

    Ok(Router::new()
        .merge(merged_routes)
        .merge(health_routes)
        .merge(settings_routes)
        .merge(auth_routes)
        .route_layer(middleware::from_fn(track_metrics))
        .layer(cors)
        .with_state(app_state))
}
