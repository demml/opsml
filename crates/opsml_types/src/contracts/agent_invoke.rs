use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvokeRequest {
    pub input: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum JobStatus {
    Pending,
    Running,
    Done,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvokeMetadata {
    pub agent_id: String,
    pub invocation: String,
    pub duration_ms: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvokeResponse {
    pub job_id: String,
    pub status: JobStatus,
    pub result: Option<serde_json::Value>,
    pub metadata: InvokeMetadata,
}
