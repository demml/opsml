use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fmt;
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct ArtifactQueryArgs {
    pub uid: Option<String>,
    pub name: Option<String>,
    pub space: Option<String>,
    pub version: Option<String>,
    pub sort_by_timestamp: Option<bool>,
    pub artifact_type: Option<ArtifactType>,
    pub limit: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct ArtifactRecord {
    pub uid: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub media_type: String,
    pub artifact_type: ArtifactType,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub enum ArtifactType {
    #[default]
    Generic,
    Figure,
}

impl fmt::Display for ArtifactType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ArtifactType::Generic => write!(f, "generic"),
            ArtifactType::Figure => write!(f, "figure"),
        }
    }
}

impl FromStr for ArtifactType {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "generic" => Ok(ArtifactType::Generic),
            "figure" => Ok(ArtifactType::Figure),
            _ => Err(()),
        }
    }
}
