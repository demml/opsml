use crate::error::TypeError;
use crate::types::RegistryType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::path::{Path, PathBuf};

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum CardTable {
    Data,
    Model,
    Experiment,
    Audit,
    Metrics,
    HardwareMetrics,
    Parameters,
    Users,
    ArtifactKey,
    AuditEvent,
    Prompt,
    Deck,
}

impl fmt::Display for CardTable {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let table_name = match self {
            CardTable::Data => "opsml_data_registry",
            CardTable::Model => "opsml_model_registry",
            CardTable::Experiment => "opsml_experiment_registry",
            CardTable::Audit => "opsml_audit_registry",
            CardTable::Metrics => "opsml_experiment_metric",
            CardTable::HardwareMetrics => "opsml_experiment_hardware_metric",
            CardTable::Parameters => "opsml_experiment_parameter",
            CardTable::Users => "opsml_user",
            CardTable::ArtifactKey => "opsml_artifact_key",
            CardTable::AuditEvent => "opsml_audit_event",
            CardTable::Prompt => "opsml_prompt_registry",
            CardTable::Deck => "opsml_deck_registry",
        };
        write!(f, "{}", table_name)
    }
}

impl CardTable {
    pub fn from_registry_type(registry_type: &RegistryType) -> Self {
        match registry_type {
            RegistryType::Data => CardTable::Data,
            RegistryType::Model => CardTable::Model,
            RegistryType::Experiment => CardTable::Experiment,
            RegistryType::Audit => CardTable::Audit,
            RegistryType::Metrics => CardTable::Metrics,
            RegistryType::HardwareMetrics => CardTable::HardwareMetrics,
            RegistryType::Parameters => CardTable::Parameters,
            RegistryType::Users => CardTable::Users,
            RegistryType::ArtifactKey => CardTable::ArtifactKey,
            RegistryType::Prompt => CardTable::Prompt,
            RegistryType::Deck => CardTable::Deck,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct CardDeckMapping {
    pub card_paths: HashMap<String, PathBuf>,
    pub drift_paths: HashMap<String, PathBuf>,
}

impl CardDeckMapping {
    pub fn new() -> Self {
        Self {
            // this will be the card alias + path
            card_paths: HashMap::new(),

            // this will be the drift alias + path (if it exists)
            drift_paths: HashMap::new(),
        }
    }

    pub fn add_card_path(&mut self, alias: &str, path: &Path) {
        self.card_paths
            .insert(alias.to_string(), path.to_path_buf());
    }
    pub fn add_drift_path(&mut self, alias: &str, path: &Path) {
        self.drift_paths
            .insert(alias.to_string(), path.to_path_buf());
    }

    pub fn from_path(path: &Path) -> Result<Self, TypeError> {
        let json_string = std::fs::read_to_string(path)?;
        let mapping: CardDeckMapping = serde_json::from_str(&json_string)?;
        Ok(mapping)
    }
}
