use crate::types::RegistryType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::fmt::Display;

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum CardTable {
    Data,
    Model,
    Run,
    Project,
    Audit,
    Pipeline,
    Metrics,
    HardwareMetrics,
    Parameters,
    Users,
    ArtifactKey,
    Operations,
}

impl fmt::Display for CardTable {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let table_name = match self {
            CardTable::Data => "opsml_data_registry",
            CardTable::Model => "opsml_model_registry",
            CardTable::Run => "opsml_run_registry",
            CardTable::Project => "opsml_project_registry",
            CardTable::Audit => "opsml_audit_registry",
            CardTable::Pipeline => "opsml_pipeline_registry",
            CardTable::Metrics => "opsml_run_metrics",
            CardTable::HardwareMetrics => "opsml_run_hardware_metrics",
            CardTable::Parameters => "opsml_run_parameters",
            CardTable::Users => "opsml_users",
            CardTable::ArtifactKey => "opsml_artifact_key",
            CardTable::Operations => "opsml_operations",
        };
        write!(f, "{}", table_name)
    }
}

impl CardTable {
    pub fn from_registry_type(registry_type: &RegistryType) -> Self {
        match registry_type {
            RegistryType::Data => CardTable::Data,
            RegistryType::Model => CardTable::Model,
            RegistryType::Run => CardTable::Run,
            RegistryType::Project => CardTable::Project,
            RegistryType::Audit => CardTable::Audit,
            RegistryType::Pipeline => CardTable::Pipeline,
            RegistryType::Metrics => CardTable::Metrics,
            RegistryType::HardwareMetrics => CardTable::HardwareMetrics,
            RegistryType::Parameters => CardTable::Parameters,
            RegistryType::Users => CardTable::Users,
            RegistryType::ArtifactKey => CardTable::ArtifactKey,
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum CardType {
    Data,
    Model,
    Run,
    Project,
    Audit,
    Pipeline,
}

impl Display for CardType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let card_type = match self {
            CardType::Data => "Data",
            CardType::Model => "Model",
            CardType::Run => "Run",
            CardType::Project => "Project",
            CardType::Audit => "Audit",
            CardType::Pipeline => "Pipeline",
        };
        write!(f, "{}", card_type)
    }
}

// implement as_bytes for CardType
impl CardType {
    pub fn as_bytes(&self) -> &[u8] {
        match self {
            CardType::Data => b"Data",
            CardType::Model => b"Model",
            CardType::Run => b"Run",
            CardType::Project => b"Project",
            CardType::Audit => b"Audit",
            CardType::Pipeline => b"Pipeline",
        }
    }
}
