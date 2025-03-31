use crate::cards::{HardwareMetrics, Metric, Parameter};
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
}

impl GetMetricRequest {
    pub fn new(experiment_uid: String, names: Option<Vec<String>>) -> Self {
        Self {
            experiment_uid,
            names: names.unwrap_or_default(),
        }
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
