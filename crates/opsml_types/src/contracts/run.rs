use crate::cards::run::types::{HardwareMetrics, Metric, Parameter};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct MetricRequest {
    pub run_uid: String,
    pub metrics: Vec<Metric>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetMetricRequest {
    pub run_uid: String,
    pub names: Vec<String>,
}

impl GetMetricRequest {
    pub fn new(run_uid: String, names: Option<Vec<String>>) -> Self {
        Self {
            run_uid,
            names: names.unwrap_or_default(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetMetricNamesRequest {
    pub run_uid: String,
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
    pub run_uid: String,
    pub parameters: Vec<Parameter>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetParameterRequest {
    pub run_uid: String,
    pub names: Vec<String>,
}

impl GetParameterRequest {
    pub fn new(run_uid: String, names: Option<Vec<String>>) -> Self {
        Self {
            run_uid,
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
    pub run_uid: String,
    pub metrics: Vec<HardwareMetrics>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetHardwareMetricRequest {
    pub run_uid: String,
}

#[derive(Serialize, Deserialize)]
pub struct HardwareMetricResponse {
    pub success: bool,
}

#[derive(Serialize, Deserialize)]
pub struct GetRunGraphsRequest {
    pub run_uid: String,
}
