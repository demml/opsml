use opsml_sql::schemas::schema::{CardSummary, QueryStats};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryPageResponse {
    pub summaries: Vec<CardSummary>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RegistryStatsResponse {
    pub stats: QueryStats,
}
