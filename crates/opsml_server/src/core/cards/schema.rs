use chrono::{DateTime, Utc};
use opsml_sql::schemas::{
    schema::{CardSummary, QueryStats},
    VersionSummary,
};
use opsml_types::{contracts::CardCursor, RegistryType};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryPageResponse {
    pub items: Vec<CardSummary>,
    pub has_next: bool,
    pub next_cursor: Option<CardCursor>,
    pub has_previous: bool,
    pub previous_cursor: Option<CardCursor>,
    pub page_info: PageInfo,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PageInfo {
    pub page_size: usize,
    pub offset: i32,
    pub filters: FilterSummary,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FilterSummary {
    pub search_term: Option<String>,
    pub spaces: Vec<String>,
    pub tags: Vec<String>,
    pub sort_by: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VersionPageResponse {
    pub summaries: Vec<VersionSummary>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RegistryStatsResponse {
    pub stats: QueryStats,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Card {
    metadata: serde_json::Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ReadeMe {
    pub readme: String,
    pub exists: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateReadeMe {
    pub space: String,
    pub name: String,
    pub registry_type: RegistryType,
    pub readme: String,
}

// create intertresponse type
pub type InsertCardResponse = (
    String,        // uid
    String,        // space
    String,        // registry type
    String,        // uri
    String,        // app env
    DateTime<Utc>, // created at
);
