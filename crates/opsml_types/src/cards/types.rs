use crate::types::{CommonKwargs, RegistryType};
use opsml_error::TypeError;
use opsml_utils::{clean_string, validate_name_repository_pattern};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::{env, fmt};

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

pub type BaseArgsResult = (String, String, String, String);

pub struct BaseArgs {}

impl BaseArgs {
    pub fn create_args(
        name: Option<&str>,
        repository: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
    ) -> Result<BaseArgsResult, TypeError> {
        let name = clean_string(&Self::get_value("NAME", name)?)?;
        let repository = clean_string(&Self::get_value("REPOSITORY", repository)?)?;

        let version = version.map_or(CommonKwargs::BaseVersion.to_string(), |v| v.to_string());
        let uid = uid.map_or(CommonKwargs::Undefined.to_string(), |v| v.to_string());

        validate_name_repository_pattern(&name, &repository)?;

        Ok((repository, name, version, uid))
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
