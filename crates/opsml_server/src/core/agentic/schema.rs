use opsml_types::contracts::tool::ToolSpec;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct ServiceToolsQuery {
    /// Target deployment environment (default: "production")
    pub environment: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ServiceToolsResponse {
    pub service_name: String,
    pub service_type: String,
    pub tools: Vec<ToolSpec>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ArtifactMeta {
    pub name: String,
    pub latest_version: String,
    pub description: Option<String>,
    pub etag: String,
    pub compatible_tools: Vec<String>,
    pub download_count: i64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MapResponse {
    pub space: String,
    pub skills: Vec<ArtifactMeta>,
    pub subagents: Vec<ArtifactMeta>,
    pub tools: Vec<ArtifactMeta>,
    pub commands: Vec<ArtifactMeta>,
    pub agents: Vec<ArtifactMeta>,
}
