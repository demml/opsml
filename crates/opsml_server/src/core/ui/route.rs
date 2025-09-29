use crate::core::state::AppState;
use anyhow::Result;
use axum::Router;
use axum::{
    http::{header::CONTENT_TYPE, StatusCode, Uri},
    response::{IntoResponse, Response},
    routing::get,
};
use rust_embed::Embed;
use std::sync::Arc;
use tracing::error;

#[derive(Embed)]
#[folder = "opsml_ui/site/"]
struct Assets;

async fn serve_sveltekit_app() -> Response {
    match Assets::get("index.html") {
        Some(content) => {
            let mime = mime_guess::from_path("index.html").first_or_octet_stream();
            ([(CONTENT_TYPE, mime.as_ref())], content.data).into_response()
        }
        None => not_found().await,
    }
}

async fn get_static_file(path: &str) -> Response {
    if path.starts_with("opsml/api/") {
        return not_found().await;
    }

    if let Some(content) = Assets::get(path) {
        let mime = mime_guess::from_path(path).first_or_octet_stream();
        return ([(CONTENT_TYPE, mime.as_ref())], content.data).into_response();
    }

    if is_dynamic_card_route(path) || is_dynamic_genai_card_route(path) {
        return serve_sveltekit_app().await;
    }

    // Check for root opsml path
    if path.starts_with("opsml/") && !path.split('/').next_back().unwrap_or("").contains('.') {
        return serve_home_html().await;
    }

    if path == "opsml" || path == "opsml/" || path.is_empty() {
        return serve_home_html().await;
    }

    not_found().await
}

fn is_dynamic_card_route(path: &str) -> bool {
    let parts: Vec<&str> = path.split('/').collect();

    // /opsml/{registry}/card/{space}/{name}/{version}
    parts.len() == 6
        && parts[0] == "opsml"
        && parts[2] == "card"
        && matches!(parts[1], "data" | "model" | "experiment" | "service")
}

fn is_dynamic_genai_card_route(path: &str) -> bool {
    let parts: Vec<&str> = path.split('/').collect();

    // /opsml/genai/{subregistry}/card/{space}/{name}/{version}
    parts.len() == 7 && parts[0] == "opsml" && parts[1] == "genai" && parts[3] == "card"
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

async fn root_redirect() -> Response {
    axum::response::Redirect::permanent("/opsml/home").into_response()
}

pub async fn get_ui_router() -> Result<Router<Arc<AppState>>> {
    Ok(Router::new()
        .route("/", get(root_redirect))
        .route("/opsml", get(opsml_home))
        .route("/opsml/home", get(opsml_home))
        .route("/opsml/{*path}", get(static_handler))
        .fallback(static_handler))
}
