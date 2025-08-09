use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct ArtifactQueryArgs {
    pub uid: Option<String>,
    pub name: Option<String>,
    pub space: Option<String>,
    pub version: Option<String>,
    pub sort_by_timestamp: Option<bool>,
    pub limit: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct ArtifactRecord {
    pub uid: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub data_type: String,
    pub created_at: DateTime<Utc>,
}
