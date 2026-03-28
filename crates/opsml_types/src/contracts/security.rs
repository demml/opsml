use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SkillScanClassification {
    Clean,
    Violation,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillScanResult {
    pub classification: SkillScanClassification,
    pub reason: String,
    #[serde(default)]
    pub findings: Vec<String>,
}

impl SkillScanResult {
    pub fn passed(&self) -> bool {
        self.classification == SkillScanClassification::Clean
    }

    pub fn from_response_value(value: Value) -> Result<Self, serde_json::Error> {
        serde_json::from_value(value)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillScanRejection {
    pub rejected: bool,
    pub reason: String,
    pub findings: Vec<String>,
}

impl SkillScanRejection {
    pub fn new(reason: String, findings: Vec<String>) -> Self {
        Self {
            rejected: true,
            reason,
            findings,
        }
    }
}
