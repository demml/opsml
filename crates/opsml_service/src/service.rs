use crate::error::ServiceError;
use opsml_state::app_state;
use opsml_types::contracts::{Card, DeploymentConfig, ServiceConfig, ServiceMetadata, ServiceType};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
const DEFAULT_SERVICE_FILENAME: &str = "opsmlspec.yml";

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
    pub metadata: Option<ServiceMetadata>,
    pub service: Option<ServiceConfig>,
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
            service: None,
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

    /// Filter the deployment configurations to only include those matching the current application environment
    /// This is important when dealing with multiple deployment environments in a single service spec
    /// We don't want to record the prod deployment config in staging or dev environments
    fn filter_deploy_by_environment(&mut self) -> Result<(), ServiceError> {
        let app_env = app_state().config()?.app_env.clone();
        if let Some(deployments) = &mut self.deploy {
            deployments.retain(|d| d.environment == app_env);
            if deployments.is_empty() {
                self.deploy = None;
            }
        }
        Ok(())
    }
    fn validate_service_type(&self) -> Result<(), ServiceError> {
        match &self.service_type {
            ServiceType::Mcp => {
                // assert that a deployment config exists
                if self.deploy.is_none() || self.deploy.as_ref().unwrap().is_empty() {
                    return Err(ServiceError::MissingDeploymentConfigForMCPService(
                        self.name.clone(),
                    ));
                }
                Ok(())
            }
            _ => Ok(()),
        }
    }

    pub fn from_env() -> Result<Self, ServiceError> {
        let current_dir = std::env::current_dir()?;
        Self::from_path(&current_dir)
    }

    fn validate(&mut self) -> Result<(), ServiceError> {
        self.validate_service_type()?;
        self.service
            .as_mut()
            .map(|service| service.validate(self.space_config.get_space(), &self.service_type))
            .transpose()?;
        Ok(())
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

        spec.filter_deploy_by_environment()?;
        spec.validate()?;
        Ok(spec)
    }

    pub fn space(&self) -> &str {
        self.space_config.get_space()
    }

    pub fn get_card(&self, alias: &str) -> Option<&Card> {
        if let Some(service) = &self.service {
            if let Some(cards) = &service.cards {
                cards.iter().find(|card| card.alias == alias)
            } else {
                None
            }
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use opsml_types::contracts::mcp::{McpCapability, McpTransport};

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
  - environment: development
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
  - environment: development
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

        let service = spec.service.unwrap();
        let mcp_config = service.mcp.as_ref().unwrap();
        assert_eq!(mcp_config.transport, McpTransport::Http);

        // check capabilities
        assert!(mcp_config.capabilities.contains(&McpCapability::Resources));
        assert!(mcp_config.capabilities.contains(&McpCapability::Tools));
    }

    #[test]
    fn test_service_spec_with_mcp_no_resources() {
        let yaml_content = r#"
name: test-service
team: my-team
type: Mcp
metadata:
  description: Test service
  language: python
  tags: [ml, test]

service:
  mcp:
    capabilities: [Resources, Tools]
    transport: Http

deploy:
  - environment: development
    endpoints: [https://test.example.com]
"#;

        let spec = ServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");
        //assert mcp type
        assert_eq!(spec.service_type, ServiceType::Mcp);

        let service = spec.service.unwrap();
        let mcp_config = service.mcp.as_ref().unwrap();
        assert_eq!(mcp_config.transport, McpTransport::Http);

        // check capabilities
        assert!(mcp_config.capabilities.contains(&McpCapability::Resources));
        assert!(mcp_config.capabilities.contains(&McpCapability::Tools));
    }
}
