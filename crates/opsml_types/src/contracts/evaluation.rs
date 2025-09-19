use serde::{Deserialize, Serialize};

use crate::contracts::ArtifactKey;

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateEvaluationRequest {
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateEvaluationResponse {
    pub uid: String,
    pub key: ArtifactKey,
}
