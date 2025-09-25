use crate::contracts::mcp::McpConfig;
use crate::error::TypeError;
use crate::RegistryType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Default)]
#[pyclass]
pub enum ServiceType {
    #[default]
    #[serde(alias = "API", alias = "api")]
    Api,
    #[serde(alias = "MCP", alias = "mcp")]
    Mcp,
    #[serde(alias = "AGENT", alias = "agent")]
    Agent,
}

impl Display for ServiceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ServiceType::Api => write!(f, "Api"),
            ServiceType::Mcp => write!(f, "Mcp"),
            ServiceType::Agent => write!(f, "Agent"),
        }
    }
}

impl From<&str> for ServiceType {
    fn from(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "api" => ServiceType::Api,
            "mcp" => ServiceType::Mcp,
            "agent" => ServiceType::Agent,
            _ => ServiceType::Api, // default to Api if unknown
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceMetadata {
    pub description: String,
    pub language: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GpuConfig {
    #[serde(rename = "type")]
    pub gpu_type: String,
    pub count: u32,
    pub memory: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Resources {
    pub cpu: u32,
    pub memory: String,
    pub storage: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gpu: Option<GpuConfig>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DeploymentConfig {
    pub environment: String,
    pub provider: Option<String>,
    pub location: Option<Vec<String>>,
    pub endpoints: Vec<String>,
    pub resources: Option<Resources>,
    pub links: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DriftConfig {
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub deactivate_others: bool,
    pub drift_type: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Card {
    pub alias: String,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub space: String,
    pub name: String,
    pub version: Option<String>,
    #[serde(rename = "type")]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift: Option<DriftConfig>,
}

impl Card {
    /// Validate the card configuration to ensure drift is only used for model cards
    pub fn validate(&self) -> Result<(), TypeError> {
        // Only allow drift configuration for model cards
        if self.drift.is_some() && self.registry_type != RegistryType::Model {
            return Err(TypeError::InvalidConfiguration);
        }
        Ok(())
    }

    /// Get the effective space for this card, falling back to the provided default space
    pub fn set_space(&mut self, service_space: &str) {
        if self.space.is_empty() {
            self.space = service_space.to_string();
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ServiceConfig {
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
    pub mcp: Option<McpConfig>,
}

impl ServiceConfig {
    pub fn validate(
        &mut self,
        service_space: &str,
        service_type: &ServiceType,
    ) -> Result<(), TypeError> {
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate()?;
                // need to set the space to overall service space if not set
                card.set_space(service_space);
            }
        }

        // if service type is MCP, ensure MCP config is provided
        if service_type == &ServiceType::Mcp && self.mcp.is_none() {
            return Err(TypeError::MissingMCPConfig);
        }
        Ok(())
    }
}
