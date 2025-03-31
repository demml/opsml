use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct GroupedMetric {
    pub uid: String,
    pub version: String,
    pub value: Vec<f64>,
    pub step: Option<Vec<i64>>,
    pub timestamp: Option<Vec<i64>>,
}
