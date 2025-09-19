use crate::contracts::ArtifactKey;
use serde::{Deserialize, Serialize};
use std::fmt::Display;

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateEvaluationRequest {
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateEvaluationResponse {
    pub uid: String,
    pub key: ArtifactKey,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum EvaluationType {
    LLM,
    Other,
}

impl Display for EvaluationType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EvaluationType::LLM => write!(f, "LLM"),
            EvaluationType::Other => write!(f, "Other"),
        }
    }
}
