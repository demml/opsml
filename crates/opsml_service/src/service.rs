use crate::error::ServiceError;
use opsml_types::RegistryType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;
use std::path::{Path, PathBuf};
const DEFAULT_SERVICE_FILENAME: &str = "opsmlspec.yml";

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
pub enum McpTransport {
    #[serde(alias = "HTTP", alias = "http")]
    Http,
    #[serde(alias = "STDIO", alias = "stdio")]
    Stdio,
}

impl Display for McpTransport {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            McpTransport::Http => write!(f, "Http"),
            McpTransport::Stdio => write!(f, "Stdio"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
pub enum McpCapability {
    #[serde(alias = "RESOURCES", alias = "resources")]
    Resources,
    #[serde(alias = "TOOLS", alias = "tools")]
    Tools,
    #[serde(alias = "PROMPTS", alias = "prompts")]
    Prompts,
}

impl Display for McpCapability {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            McpCapability::Resources => write!(f, "Resources"),
            McpCapability::Tools => write!(f, "Tools"),
            McpCapability::Prompts => write!(f, "Prompts"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
#[pyclass]
pub enum ServiceType {
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
pub struct McpConfig {
    pub capabilities: Vec<McpCapability>,
    pub transport: McpTransport,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ServiceConfig {
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
    pub mcp: Option<McpConfig>,
}

impl ServiceConfig {
    fn validate(
        &mut self,
        service_space: &str,
        service_type: &ServiceType,
    ) -> Result<(), ServiceError> {
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate()?;
                // need to set the space to overall service space if not set
                card.set_space(service_space);
            }
        }

        // if service type is MCP, ensure MCP config is provided
        if service_type == &ServiceType::Mcp && self.mcp.is_none() {
            return Err(ServiceError::MissingMCPConfig);
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
    pub metadata: Option<Metadata>,
    pub service: ServiceConfig,
    pub deploy: Option<Vec<DeploymentConfig>>,

    #[serde(skip)]
    pub root_path: PathBuf,
}

impl ServiceSpec {
    pub fn new_empty(
        name: &str,
        space: &str,
        service_type: ServiceType,
    ) -> Result<Self, ServiceError> {
        let mut spec = ServiceSpec {
            name: name.to_string(),
            space_config: SpaceConfig::Space {
                space: space.to_string(),
            },
            service_type,
            metadata: None,
            service: ServiceConfig::default(),
            deploy: None,
            root_path: PathBuf::new(),
        };
        spec.validate()?;
        Ok(spec)
    }
    /// Load a ServiceSpec from a file path, searching parent directories if necessary.
    /// This method is used within the CLI to locate the service specification file.
    /// # Arguments
    /// * `path` - Optional path to the spec file or directory. If None, uses current directory.
    ///   - If the path is a file, loads that file directly.
    ///   - If the path is a directory, searches for `opsmlspec.yml`.
    /// # Returns
    /// * `ServiceSpec` - The loaded service specification
    pub fn from_path(path: &Path) -> Result<Self, ServiceError> {
        // We are returning both the service spec and the root path where the spec was found
        // This is useful for (1) loading the spec file and (2) determine which root path a spec belongs to
        // This is import for the CLI where we create a lock file in the root path
        let (service_path, root_path) = {
            if path.is_file() {
                // (1) If user provides a file path, just return that file
                let root_path = path
                    .parent()
                    .ok_or_else(|| {
                        ServiceError::MissingServiceFile("Invalid file path".to_string())
                    })?
                    .to_path_buf();
                (path.to_path_buf(), root_path)
            } else if path.is_dir() {
                // (2) If user provides a directory, search for our the opsmlspec.yml file in that directory or its parents
                let root_path = path
                    .ancestors()
                    .find(|dir| dir.join(DEFAULT_SERVICE_FILENAME).is_file())
                    .ok_or_else(|| {
                        ServiceError::MissingServiceFile(DEFAULT_SERVICE_FILENAME.to_string())
                    })?
                    .to_path_buf();

                let service_path = root_path.join(DEFAULT_SERVICE_FILENAME);
                (service_path, root_path)
            } else {
                // (3) If user provides an invalid path let the error bubble up
                Err(ServiceError::MissingServiceFile(format!(
                    "Invalid file path: {}",
                    path.display()
                )))?
            }
        };

        let mut spec = Self::from_yaml_file(&service_path)?;
        spec.root_path = root_path;

        Ok(spec)
    }

    pub fn from_env() -> Result<Self, ServiceError> {
        let current_dir = std::env::current_dir()?;
        Self::from_path(&current_dir)
    }

    fn validate(&mut self) -> Result<(), ServiceError> {
        self.service
            .validate(self.space_config.get_space(), &self.service_type)
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
    fn test_service_spec_with_api() {
        let yaml_content = r#"
name: test-service
team: my-team
type: Api
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

    #[test]
    fn test_service_spec_with_mcp() {
        let yaml_content = r#"
name: test-service
team: my-team
type: Mcp
metadata:
  description: Test service
  language: python
  tags: [ml, test]

service:
  version: "1.0.0"
  write_dir: "opsml_app/test_service"
  mcp:
    capabilities: [Resources, Tools]
    transport: Http

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
        //assert mcp type
        assert_eq!(spec.service_type, ServiceType::Mcp);

        let mcp_config = spec.service.mcp.as_ref().unwrap();
        assert_eq!(mcp_config.transport, McpTransport::Http);

        // check capabilities
        assert!(mcp_config.capabilities.contains(&McpCapability::Resources));
        assert!(mcp_config.capabilities.contains(&McpCapability::Tools));
    }
}
