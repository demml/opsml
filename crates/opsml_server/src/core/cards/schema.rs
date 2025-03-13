use opsml_sql::schemas::schema::{CardSummary, QueryStats};
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryPageResponse {
    pub summaries: Vec<CardSummary>,
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
    pub repository: String,
    pub name: String,
    pub registry_type: RegistryType,
    pub readme: String,
}
