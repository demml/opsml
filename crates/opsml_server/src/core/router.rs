use crate::core::agentic::route::get_agentic_router;
use crate::core::auth::middleware::auth_api_middleware;
use crate::core::auth::route::get_auth_router;
use crate::core::capabilities::route::get_capabilities_router;
use crate::core::cards::route::get_card_router;
use crate::core::debug::route::get_debug_router;
use crate::core::docs::route::get_docs_router;
use crate::core::experiment::route::get_experiment_router;
use crate::core::files::route::get_file_router;
use crate::core::genai::route::get_genai_router;
use crate::core::health::route::get_health_router;
use crate::core::middleware::event::event_middleware;
use crate::core::middleware::metrics::track_metrics;
use crate::core::openapi::ApiDoc;
use crate::core::scouter::route::get_scouter_router;
use crate::core::settings::route::get_settings_router;
use crate::core::state::AppState;
use crate::core::user::route::get_user_router;
use anyhow::Result;
use axum::http::{
    HeaderName, HeaderValue, Method,
    header::{ACCEPT, AUTHORIZATION, CONTENT_TYPE},
};
use axum::{Router, middleware, response::Response};
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

const ROUTE_PREFIX: &str = "/opsml/api";
const V1_PREFIX: &str = "/opsml/api/v1";

async fn set_version_headers(mut response: Response) -> Response {
    let headers = response.headers_mut();
    headers.insert(
        HeaderName::from_static("x-opsml-api-version"),
        HeaderValue::from_static("1.0"),
    );
    headers.insert(
        HeaderName::from_static("x-opsml-server-version"),
        HeaderValue::from_static(env!("CARGO_PKG_VERSION")),
    );
    response
}

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
    let agentic_routes = get_agentic_router(ROUTE_PREFIX).await?;
    let docs_routes = get_docs_router(V1_PREFIX).await?;
    let capabilities_routes = get_capabilities_router(V1_PREFIX).await?;

    // All routes except auth, healthcheck, settings, docs, and capabilities are protected.
    let merged_routes = Router::new()
        .merge(debug_routes)
        .merge(file_routes)
        .merge(card_routes)
        .merge(run_routes)
        .merge(user_routes)
        .merge(scouter_routes)
        .merge(genai_routes)
        .merge(agentic_routes)
        .route_layer(middleware::from_fn_with_state(
            app_state.clone(),
            event_middleware,
        ))
        .route_layer(middleware::from_fn_with_state(
            app_state.clone(),
            auth_api_middleware,
        ));

    // Build the stateful router, then merge the stateless Swagger UI on top.
    // SwaggerUi is Into<Router<()>>; merging after .with_state() keeps types aligned.
    let stateful = Router::new()
        .merge(merged_routes)
        .merge(health_routes)
        .merge(settings_routes)
        .merge(auth_routes)
        .merge(docs_routes)
        .merge(capabilities_routes)
        .layer(middleware::map_response(set_version_headers))
        .route_layer(middleware::from_fn(track_metrics))
        .layer(cors)
        .with_state(app_state);

    let swagger = SwaggerUi::new(format!("{V1_PREFIX}/docs/ui"))
        .url(format!("{V1_PREFIX}/openapi.json"), ApiDoc::openapi());

    Ok(stateful.merge(swagger))
}
