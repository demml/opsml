use crate::core::state::AppState;
use crate::core::ui::schema::CardsRequest;
use anyhow::Result;
use axum::extract::{Path, Query};
use axum::Router;
use axum::{
    http::{header::CONTENT_TYPE, StatusCode, Uri},
    response::{IntoResponse, Response},
    routing::get,
};
use rust_embed::Embed;
use serde::Deserialize;
use std::sync::Arc;
use tracing::{debug, error, info};

#[derive(Embed)]
#[folder = "opsml_ui/site/"]
struct Assets;

#[derive(Deserialize)]
struct CardPath {
    path: String,
}

#[derive(Deserialize)]
struct NestedCardPath {
    path: String,
    subpath: String,
}

async fn get_static_file(path: &str) -> Response {
    if path.starts_with("opsml/api/") {
        return not_found().await;
    }

    // Check for root opsml path
    if path == "opsml" || path == "opsml/" {
        debug!("Matched /opsml path, serving home.html");
        return serve_home_html().await;
    }

    // Handle empty path
    if path.is_empty() {
        info!("Empty path, serving home.html");
        return serve_home_html().await;
    }

    match Assets::get(path) {
        Some(content) => {
            let mime = mime_guess::from_path(path).first_or_octet_stream();
            ([(CONTENT_TYPE, mime.as_ref())], content.data).into_response()
        }
        None => {
            if path.contains('.') {
                return not_found().await;
            }

            // SPA routes - serve home.html
            if path.starts_with("opsml/") && !path.contains('.') {
                return serve_home_html().await;
            }

            serve_home_html().await
        }
    }
}

async fn static_handler(uri: Uri) -> impl IntoResponse {
    let path = uri.path().trim_start_matches('/');
    get_static_file(path).await
}

async fn serve_home_html() -> Response {
    match Assets::get("opsml/home.html") {
        Some(content) => {
            let mime = mime_guess::from_path("home.html").first_or_octet_stream();
            ([(CONTENT_TYPE, mime.as_ref())], content.data).into_response()
        }
        None => {
            error!("opsml/home.html not found!");
            not_found().await
        }
    }
}

async fn not_found() -> Response {
    (StatusCode::NOT_FOUND, "404").into_response()
}

async fn opsml_home() -> impl IntoResponse {
    get_static_file("opsml/home.html").await
}

async fn opsml_card_page(
    Path(path_params): Path<CardPath>,
    Query(_params): Query<CardsRequest>,
) -> impl IntoResponse {
    debug!("Card request for path: {}", path_params.path);

    // Now you can use the path parameter
    let html_path = format!("opsml/{}.html", path_params.path);

    get_static_file(&html_path).await
}

async fn opsml_card_entity_page(
    Path(path_params): Path<NestedCardPath>,
    Query(_params): Query<CardsRequest>,
) -> impl IntoResponse {
    debug!("Card request for path: {}", path_params.path);

    // Now you can use the path parameter
    // Construct the HTML path with both parameters
    let html_path = format!(
        "opsml/{}/card/{}.html",
        path_params.path, path_params.subpath
    );
    get_static_file(&html_path).await
}

pub async fn get_ui_router() -> Result<Router<Arc<AppState>>> {
    Ok(Router::new()
        .route("/", get(opsml_home))
        .route("/opsml", get(opsml_home))
        .route("/opsml/home", get(opsml_home))
        .route("/opsml/{path}", get(opsml_card_page))
        .route("/opsml/{path}/card/{subpath}", get(opsml_card_entity_page))
        .fallback(static_handler))
}
