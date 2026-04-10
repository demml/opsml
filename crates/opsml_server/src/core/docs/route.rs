use crate::core::error::OpsmlServerError;
use anyhow::Result;
use axum::extract::{Path, Query};
use axum::http::StatusCode;
use axum::{Json, Router, routing::get};
use opsml_mcp::content::DOCS;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use utoipa::ToSchema;

use crate::core::state::AppState;

/// Returns the largest byte index ≤ `i` that lies on a UTF-8 character boundary in `s`.
fn floor_char_boundary(s: &str, i: usize) -> usize {
    let mut idx = i.min(s.len());
    while idx > 0 && !s.is_char_boundary(idx) {
        idx -= 1;
    }
    idx
}

#[derive(Serialize, ToSchema)]
pub struct DocSummary {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
}

#[derive(Serialize, ToSchema)]
pub struct DocListResponse {
    pub docs: Vec<DocSummary>,
}

#[derive(Serialize, ToSchema)]
pub struct DocResponse {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
    pub content: &'static str,
}

#[derive(Deserialize, utoipa::IntoParams)]
pub struct SearchQuery {
    /// Search term matched case-insensitively against doc titles and content. Max 200 characters.
    pub q: String,
}

#[derive(Serialize, ToSchema)]
pub struct SearchResult {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
    pub snippet: String,
}

#[derive(Serialize, ToSchema)]
pub struct SearchResponse {
    pub query: String,
    pub results: Vec<SearchResult>,
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/docs",
    responses(
        (status = 200, description = "List of all documentation entries", body = DocListResponse),
    ),
    tag = "docs"
)]
pub async fn list_docs() -> Json<DocListResponse> {
    let docs = DOCS
        .iter()
        .filter(|e| e.category != "example")
        .map(|e| DocSummary {
            id: e.id,
            title: e.title,
            category: e.category,
        })
        .collect();
    Json(DocListResponse { docs })
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/docs/{id}",
    params(
        ("id" = String, Path, description = "Slash-separated doc path, e.g. 'cards/datacard' or 'setup/overview'. Matches multiple path segments. Call GET /v1/docs to list all IDs.")
    ),
    responses(
        (status = 200, description = "Full documentation content", body = DocResponse),
        (status = 404, description = "Doc not found", body = OpsmlServerError),
    ),
    tag = "docs"
)]
pub async fn get_doc(
    Path(id): Path<String>,
) -> Result<Json<DocResponse>, (StatusCode, Json<OpsmlServerError>)> {
    DOCS.iter()
        .find(|e| e.category != "example" && e.id == id.as_str())
        .map(|e| {
            Json(DocResponse {
                id: e.id,
                title: e.title,
                category: e.category,
                content: e.content,
            })
        })
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::not_found(&format!("Doc '{id}'"))),
            )
        })
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/docs/search",
    params(SearchQuery),
    responses(
        (status = 200, description = "Matching docs with snippets", body = SearchResponse),
        (status = 400, description = "Search query too long", body = OpsmlServerError),
    ),
    tag = "docs"
)]
pub async fn search_docs(
    Query(params): Query<SearchQuery>,
) -> Result<Json<SearchResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if params.q.len() > 200 {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(OpsmlServerError::bad_request("Search query exceeds 200 character limit")),
        ));
    }

    let q = params.q.to_lowercase();
    let results = DOCS
        .iter()
        .filter_map(|e| {
            let content_lower = e.content.to_lowercase();
            let title_lower = e.title.to_lowercase();
            if !title_lower.contains(&q) && !content_lower.contains(&q) {
                return None;
            }
            let snippet = if let Some(pos) = content_lower.find(&q) {
                // Compute char-boundary-aligned slice on content_lower (same byte domain as pos).
                let start = floor_char_boundary(&content_lower, pos.saturating_sub(80));
                let end = floor_char_boundary(&content_lower, (pos + q.len() + 80).min(content_lower.len()));
                format!("...{}...", &content_lower[start..end])
            } else {
                e.title.to_string()
            };
            Some(SearchResult {
                id: e.id,
                title: e.title,
                category: e.category,
                snippet,
            })
        })
        .collect();

    Ok(Json(SearchResponse {
        query: params.q,
        results,
    }))
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/examples",
    responses(
        (status = 200, description = "List of all Python example entries", body = DocListResponse),
    ),
    tag = "docs"
)]
pub async fn list_examples() -> Json<DocListResponse> {
    let docs = DOCS
        .iter()
        .filter(|e| e.category == "example")
        .map(|e| DocSummary {
            id: e.id,
            title: e.title,
            category: e.category,
        })
        .collect();
    Json(DocListResponse { docs })
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/examples/{id}",
    params(
        ("id" = String, Path, description = "Slash-separated example path, e.g. 'data/pandas' or 'model/sklearn'. Matches multiple path segments. Call GET /v1/examples to list all IDs.")
    ),
    responses(
        (status = 200, description = "Python example source code", body = DocResponse),
        (status = 404, description = "Example not found", body = OpsmlServerError),
    ),
    tag = "docs"
)]
pub async fn get_example(
    Path(id): Path<String>,
) -> Result<Json<DocResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let full_id = format!("example/{id}");
    DOCS.iter()
        .find(|e| e.category == "example" && e.id == full_id.as_str())
        .map(|e| {
            Json(DocResponse {
                id: e.id,
                title: e.title,
                category: e.category,
                content: e.content,
            })
        })
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::not_found(&format!("Example '{id}'"))),
            )
        })
}

pub async fn get_docs_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    Ok(Router::new()
        .route(&format!("{prefix}/docs"), get(list_docs))
        .route(&format!("{prefix}/docs/search"), get(search_docs))
        .route(&format!("{prefix}/docs/{{*id}}"), get(get_doc))
        .route(&format!("{prefix}/examples"), get(list_examples))
        .route(&format!("{prefix}/examples/{{*id}}"), get(get_example)))
}
