use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
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
    /// Reserved for tool cards (ToolCard — PR 7). Always empty until then.
    pub tools: Vec<ArtifactMeta>,
    /// Reserved for agent configs (AgentSpec — PR 7). Always empty until then.
    pub agents: Vec<ArtifactMeta>,
}
