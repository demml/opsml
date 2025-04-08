use crate::types::{CommonKwargs, RegistryType};
use opsml_error::TypeError;
use opsml_utils::{clean_string, validate_name_space_pattern};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::{env, fmt};

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

pub type BaseArgsResult = (String, String, String, String);

pub struct BaseArgs {}

impl BaseArgs {
    pub fn create_args(
        name: Option<&str>,
        space: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
    ) -> Result<BaseArgsResult, TypeError> {
        let name = clean_string(&Self::get_value("NAME", name)?)?;
        let space = clean_string(&Self::get_value("space", space)?)?;

        let version = version.map_or(CommonKwargs::BaseVersion.to_string(), |v| v.to_string());
        let uid = uid.map_or(CommonKwargs::Undefined.to_string(), |v| v.to_string());

        validate_name_space_pattern(&name, &space)?;

        Ok((space, name, version, uid))
    }

    fn get_value(key: &str, value: Option<&str>) -> Result<String, TypeError> {
        let uppercase = key.to_uppercase();
        let env_key = format!("OPSML_RUNTIME_{uppercase}");
        let env_val = env::var(&env_key).ok();

        value
            .as_ref()
            .map(|s| s.to_string())
            .or(env_val)
            .ok_or_else(|| TypeError::Error(format!("{key} not provided")))
    }
}
