use crate::error::ServiceError;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

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
    #[serde(skip_serializing_if = "Option::is_none")]
    pub space: Option<String>,
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
    pub fn get_effective_space(&self, default_space: &str) -> String {
        self.space
            .as_ref()
            .unwrap_or(&default_space.to_string())
            .clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceConfig {
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
}

impl ServiceConfig {
    pub fn validate(&self, default_space: &str) -> Result<(), ServiceError> {
        if let Some(cards) = &self.cards {
            for card in cards {
                card.validate()?;
                // Ensure the card has an effective space
                let _ = card.get_effective_space(default_space);
            }
        }
        Ok(())
    }

    pub fn get_cards(&self, default_space: &str) -> Vec<Card> {
        if let Some(cards) = &self.cards {
            cards
                .iter()
                .map(|card| {
                    let mut card_clone = card.clone();
                    if card_clone.space.is_none() {
                        card_clone.space = Some(default_space.to_string());
                    }
                    card_clone
                })
                .collect()
        } else {
            vec![]
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Metadata {
    pub description: String,
    #[serde(flatten)]
    pub space_config: SpaceConfig,
    pub language: String,
    #[serde(rename = "type")]
    pub service_type: String,
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
    pub metadata: Metadata,
    pub service: ServiceConfig,
    pub deploy: Vec<DeploymentConfig>,
}

impl ServiceSpec {
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
        let spec: ServiceSpec = serde_yaml::from_str(yaml_str)?;
        Ok(spec)
    }

    pub fn space(&self) -> &str {
        self.metadata.space_config.get_space()
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
metadata:
  description: Test service
  team: my-team
  language: python
  type: ml-service
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
        assert_eq!(model_card.space.as_ref().unwrap(), "my-team");

        let prompt_card = spec.get_card("test_prompt").unwrap();
        assert_eq!(prompt_card.space.as_ref().unwrap(), "custom-space");
    }
}
