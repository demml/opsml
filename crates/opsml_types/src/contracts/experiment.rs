use crate::cards::{HardwareMetrics, Metric, Parameter};
use crate::contracts::{traits::AuditableRequest, ResourceType};
use crate::RegistryType;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct MetricRequest {
    pub experiment_uid: String,
    pub metrics: Vec<Metric>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetMetricRequest {
    pub experiment_uid: String,
    pub names: Vec<String>,
    #[serde(default)]
    pub is_eval: Option<bool>,
}

impl GetMetricRequest {
    pub fn new(experiment_uid: String, names: Option<Vec<String>>, is_eval: Option<bool>) -> Self {
        Self {
            experiment_uid,
            names: names.unwrap_or_default(),
            is_eval,
        }
    }
}

impl AuditableRequest for GetMetricRequest {
    fn get_resource_id(&self) -> String {
        self.experiment_uid.clone()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize GetMetricRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(RegistryType::Experiment)
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Experiment {
    pub uid: String,
    pub version: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UiMetricRequest {
    pub experiments: Vec<Experiment>,
    pub metric_names: Vec<String>,
    #[serde(default)]
    pub is_eval: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetMetricNamesRequest {
    pub experiment_uid: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetMetricNamesResponse {
    pub names: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub struct MetricResponse {
    pub success: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ParameterRequest {
    pub experiment_uid: String,
    pub parameters: Vec<Parameter>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetParameterRequest {
    pub experiment_uid: String,
    pub names: Vec<String>,
}

impl GetParameterRequest {
    pub fn new(experiment_uid: String, names: Option<Vec<String>>) -> Self {
        Self {
            experiment_uid,
            names: names.unwrap_or_default(),
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct ParameterResponse {
    pub success: bool,
}

#[derive(Serialize, Deserialize)]
pub struct HardwareMetricRequest {
    pub experiment_uid: String,
    pub metrics: HardwareMetrics,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetHardwareMetricRequest {
    pub experiment_uid: String,
}

#[derive(Serialize, Deserialize)]
pub struct HardwareMetricResponse {
    pub success: bool,
}
