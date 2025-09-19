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
#[cfg_attr(feature = "server", derive(sqlx::Type))]
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

impl std::str::FromStr for EvaluationType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "LLM" => Ok(EvaluationType::LLM),
            "Other" => Ok(EvaluationType::Other),
            _ => Err(format!("Unknown EvaluationType: {}", s)),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
#[cfg_attr(feature = "server", derive(sqlx::Type))]
pub enum EvaluationProvider {
    Opsml,
    Pydantic,
}

impl Display for EvaluationProvider {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EvaluationProvider::Opsml => write!(f, "Opsml"),
            EvaluationProvider::Pydantic => write!(f, "Pydantic"),
        }
    }
}

impl std::str::FromStr for EvaluationProvider {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "Opsml" => Ok(EvaluationProvider::Opsml),
            "Pydantic" => Ok(EvaluationProvider::Pydantic),
            _ => Err(format!("Unknown EvaluationProvider: {}", s)),
        }
    }
}
