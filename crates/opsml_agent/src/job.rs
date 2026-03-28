use chrono::{DateTime, Utc};
use opsml_types::contracts::JobStatus;
use serde_json::Value;

#[derive(Debug, Clone)]
pub struct JobState {
    pub id: String,
    pub agent_id: String,
    pub status: JobStatus,
    pub result: Option<Value>,
    pub error: Option<String>,
    pub created_at: DateTime<Utc>,
    pub duration_ms: Option<u64>,
}

impl JobState {
    pub fn new(id: String, agent_id: String) -> Self {
        Self {
            id,
            agent_id,
            status: JobStatus::Pending,
            result: None,
            error: None,
            created_at: Utc::now(),
            duration_ms: None,
        }
    }
}
