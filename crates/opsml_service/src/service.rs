use crate::error::ServiceError;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "UPPERCASE")]
pub enum ServiceType {
    Api,
    Mcp,
    Agent,
}

impl Display for ServiceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ServiceType::Api => write!(f, "API"),
            ServiceType::Mcp => write!(f, "MCP"),
            ServiceType::Agent => write!(f, "AGENT"),
        }
    }
}

impl std::str::FromStr for ServiceType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "API" => Ok(ServiceType::Api),
            "MCP" => Ok(ServiceType::Mcp),
            "AGENT" => Ok(ServiceType::Agent),
            _ => Err(format!("Unknown ServiceType: {}", s)),
        }
    }
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
    pub provider: String,
    pub location: Vec<String>,
    pub endpoints: Vec<String>,
    pub resources: Resources,
    pub links: HashMap<String, String>,
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
    pub fn validate(&self) -> Result<(), ServiceError> {
        // Only allow drift configuration for model cards
        if self.drift.is_some() && self.registry_type != RegistryType::Model {
            return Err(ServiceError::InvalidConfiguration);
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

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceConfig {
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
}

impl ServiceConfig {
    pub fn validate(&mut self, service_space: &str) -> Result<(), ServiceError> {
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate()?;
                // need to set the space to overall service space if not set
                card.set_space(service_space);
            }
        }
        Ok(())
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Metadata {
    pub description: String,
    pub language: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum SpaceConfig {
    Team { team: String },
    Space { space: String },
}

impl SpaceConfig {
    pub fn get_space(&self) -> &str {
        match self {
            SpaceConfig::Team { team } => team,
            SpaceConfig::Space { space } => space,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceSpec {
    pub name: String,
    #[serde(flatten)]
    pub space_config: SpaceConfig,
    #[serde(rename = "type")]
    pub service_type: ServiceType,
    pub metadata: Metadata,
    pub service: ServiceConfig,
    pub deploy: Vec<DeploymentConfig>,
}

impl ServiceSpec {
    fn validate(&mut self) -> Result<(), ServiceError> {
        self.service.validate(self.space_config.get_space())
    }
    /// Load a ServiceSpec from a YAML file at the given path
    /// # Arguments
    /// * `path` - Path to the YAML file
    /// # Returns
    /// * `ServiceSpec` - The loaded service specification
    pub fn from_yaml_file(path: &Path) -> Result<Self, ServiceError> {
        Self::from_yaml(&std::fs::read_to_string(path)?)
    }

    /// Load a ServiceSpec from a YAML string
    /// # Arguments
    /// * `yaml_str` - The YAML string
    /// # Returns
    /// * `ServiceSpec` - The loaded service specification
    pub fn from_yaml(yaml_str: &str) -> Result<Self, ServiceError> {
        let mut spec: ServiceSpec = serde_yaml::from_str(yaml_str)?;
        spec.validate()?;
        Ok(spec)
    }

    pub fn space(&self) -> &str {
        self.space_config.get_space()
    }

    pub fn get_card(&self, alias: &str) -> Option<&Card> {
        if let Some(cards) = &self.service.cards {
            cards.iter().find(|card| card.alias == alias)
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_spec_with_team() {
        let yaml_content = r#"
name: test-service
team: my-team
type: API
metadata:
  description: Test service
  language: python
  tags: [ml, test]

service:
  version: "1.0.0"
  write_dir: "opsml_app/test_service"
  cards:
    - alias: test_model
      name: test-model
      version: "1.*"
      type: model
      drift:
        active: true
        deactivate_others: false
        drift_type: ["psi"]
    - alias: test_prompt
      space: custom-space
      name: test-prompt
      version: "1.*"
      type: prompt

deploy:
  - environment: production
    provider: gcp
    location: [us-central1]
    endpoints: [https://test.example.com]
    resources:
      cpu: 4
      memory: 16Gi
      storage: 100Gi
    links:
      logging: https://logging.example.com
"#;

        let spec = ServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");

        let model_card = spec.get_card("test_model").unwrap();
        assert_eq!(model_card.space, "my-team");

        let prompt_card = spec.get_card("test_prompt").unwrap();
        assert_eq!(prompt_card.space, "custom-space");
    }
}
