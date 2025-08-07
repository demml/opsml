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

async fn get_static_file(path: &str) -> Response {
    if path.starts_with("opsml/api/") {
        return not_found().await;
    }

    if let Some(content) = Assets::get(path) {
        println!("Serving static file: {}", path);
        let mime = mime_guess::from_path(path).first_or_octet_stream();
        return ([(CONTENT_TYPE, mime.as_ref())], content.data).into_response();
    }

    if is_dynamic_card_route(path) {
        let redirect_path = format!("{}/home", path);
        return axum::response::Redirect::permanent(&format!("/{}", redirect_path)).into_response();
    }

    // Check for root opsml path
    if path.starts_with("opsml/") && !path.split('/').last().unwrap_or("").contains('.') {
        return serve_home_html().await;
    }

    if path == "opsml" || path == "opsml/" || path.is_empty() {
        return serve_home_html().await;
    }

    not_found().await
}

fn is_dynamic_card_route(path: &str) -> bool {
    let parts: Vec<&str> = path.split('/').collect();
    parts.len() == 6
        && parts[0] == "opsml"
        && parts[2] == "card"
        && matches!(
            parts[1],
            "data" | "model" | "experiment" | "prompt" | "service"
        )
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
