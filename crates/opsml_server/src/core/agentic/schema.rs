use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, utoipa::ToSchema)]
pub struct ArtifactMeta {
    pub name: String,
    pub latest_version: String,
    pub description: Option<String>,
    pub etag: String,
    pub compatible_tools: Vec<String>,
    pub download_count: i64,
}

#[derive(Debug, Serialize, Deserialize, utoipa::ToSchema)]
pub struct MapResponse {
    pub space: String,
    pub skills: Vec<ArtifactMeta>,
    pub subagents: Vec<ArtifactMeta>,
    pub tools: Vec<ArtifactMeta>,
    pub commands: Vec<ArtifactMeta>,
    pub agents: Vec<ArtifactMeta>,
}
