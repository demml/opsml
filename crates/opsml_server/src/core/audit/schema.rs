use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct AuditError {
    pub error: String,
    pub message: String,
}
