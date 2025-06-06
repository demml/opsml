use crate::types::RegistryType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;

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
