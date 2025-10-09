use axum::response::IntoResponse;
use axum::Json;
use serde::{Deserialize, Serialize};
use std::sync::atomic::AtomicUsize;
use std::sync::Arc;

#[derive(Serialize, Deserialize)]
pub struct DebugInfo {
    pub storage_client: String,
    pub opsml_storage_uri: String,
    pub opsml_tracking_uri: String,
}

impl DebugInfo {
    pub fn new(
        storage_client: String,
        opsml_storage_uri: String,
        opsml_tracking_uri: String,
    ) -> Self {
        Self {
            storage_client,
            opsml_storage_uri,
            opsml_tracking_uri,
        }
    }
}

// Implement IntoResponse for Alive
impl IntoResponse for DebugInfo {
    fn into_response(self) -> axum::response::Response {
        Json(self).into_response()
    }
}

#[derive(Serialize, Default)]
pub struct ConnectionInfo {
    pub connections: Vec<String>,
    pub total_connections: Arc<AtomicUsize>,
    pub peak_connections: Arc<AtomicUsize>,
    pub api_connections: Arc<AtomicUsize>,
    pub spa_connections: Arc<AtomicUsize>,
    pub request_counter: Arc<AtomicUsize>,
}

impl ConnectionInfo {
    pub fn not_implemented() -> Self {
        Self {
            connections: vec!["Connection tracking not enabled".to_string()],
            ..Default::default()
        }
    }
}

impl IntoResponse for ConnectionInfo {
    fn into_response(self) -> axum::response::Response {
        Json(self).into_response()
    }
}
