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

#[derive(Deserialize, ToSchema)]
pub struct SearchQuery {
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
        ("id" = String, Path, description = "Doc ID, e.g. 'cards/datacard' or 'setup/overview'. Call GET /v1/docs to list all IDs.")
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
    params(
        ("q" = String, Query, description = "Search query — matched case-insensitively against doc titles and content")
    ),
    responses(
        (status = 200, description = "Matching docs with snippets", body = SearchResponse),
    ),
    tag = "docs"
)]
pub async fn search_docs(Query(params): Query<SearchQuery>) -> Json<SearchResponse> {
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
                let start = pos.saturating_sub(80);
                let end = (pos + q.len() + 80).min(e.content.len());
                format!("...{}...", &e.content[start..end])
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

    Json(SearchResponse {
        query: params.q,
        results,
    })
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
        ("id" = String, Path, description = "Example path, e.g. 'data/pandas' or 'model/sklearn'. Call GET /v1/examples to list all IDs.")
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
