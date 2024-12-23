use axum::response::IntoResponse;
use axum::Json;
/// file containing schema for health module
use serde::{Deserialize, Serialize};

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
