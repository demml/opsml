use crate::error::ServiceError;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DriftConfig {
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub deactivate_others: bool,
    pub drift_type: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Card {
    pub alias: String,
    pub space: String,
    pub name: String,
    pub version: Option<String>,
    #[serde(rename = "type")]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift: Option<DriftConfig>,
}

impl Card {
    /// Validate the card configuration to ensure drift is only used for model cards
    pub fn validate(&self) -> Result<(), ServiceError> {
        // Only allow drift configuration for model cards
        if self.drift.is_some() && self.registry_type != RegistryType::Model {
            return Err(ServiceError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceConfig {
    pub name: String,
    pub space: String,
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
}
