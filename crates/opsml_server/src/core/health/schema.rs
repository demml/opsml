use axum::response::IntoResponse;
use axum::Json;
/// file containing schema for health module
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Alive {
    pub status: String,
}

impl Default for Alive {
    fn default() -> Self {
        Self {
            status: "Alive".to_string(),
        }
    }
}

// Implement IntoResponse for Alive
impl IntoResponse for Alive {
    fn into_response(self) -> axum::response::Response {
        Json(self).into_response()
    }
}
