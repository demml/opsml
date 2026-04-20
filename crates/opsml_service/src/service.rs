use crate::error::ServiceError;
use opsml_state::app_state;
use opsml_types::contracts::{
    CardVariant, DeploymentConfig, ServiceConfig, ServiceMetadata, ServiceType,
};
#[cfg(feature = "python")]
use opsml_utils::PyHelperFuncs;
#[cfg(feature = "python")]
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
pub const DEFAULT_SERVICE_FILENAME: &str = "opsmlspec.yaml";
use tracing::{error, instrument};

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
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

#[cfg(feature = "python")]
#[pymethods]
impl SpaceConfig {
    #[new]
    fn new(team: Option<String>, space: Option<String>) -> Self {
        if let Some(space) = space {
            SpaceConfig::Space { space }
        } else if let Some(team) = team {
            SpaceConfig::Team { team }
        } else {
            SpaceConfig::Team {
                team: String::new(),
            }
        }
    }
}

/// Top level specification for OpML
#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
pub struct OpsmlServiceSpec {
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

impl OpsmlServiceSpec {
    pub fn new_empty(
        name: &str,
        space: &str,
        service_type: ServiceType,
    ) -> Result<Self, ServiceError> {
        let spec = OpsmlServiceSpec {
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

        Ok(spec)
    }

    /// Load a OpsmlServiceSpec from a file path, searching parent directories if necessary.
    #[instrument(skip_all)]
    pub fn from_path(path: &Path) -> Result<Self, ServiceError> {
        let (service_path, root_path) = {
            if path.is_file() {
                let root_path = path
                    .parent()
                    .ok_or_else(|| {
                        ServiceError::MissingServiceFile("Invalid file path".to_string())
                    })?
                    .to_path_buf();
                (path.to_path_buf(), root_path)
            } else if path.is_dir() {
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
                Err(ServiceError::MissingServiceFile(format!(
                    "Invalid file path: {}",
                    path.display()
                )))?
            }
        };

        let mut spec = Self::from_yaml_file(&service_path).inspect_err(|e| {
            error!(
                "Failed to load service spec from path {}: {}",
                service_path.display(),
                e
            );
        })?;

        spec.root_path = root_path;

        spec.resolve().inspect_err(|e| {
            error!(
                "Failed to resolve service spec from path {}: {}",
                service_path.display(),
                e
            );
        })?;

        spec.validate().inspect_err(|e| {
            error!(
                "Failed to validate service spec from path {}: {}",
                service_path.display(),
                e
            );
        })?;

        Ok(spec)
    }

    #[instrument(skip_all)]
    fn resolve(&mut self) -> Result<(), ServiceError> {
        if let Some(service) = &mut self.service {
            service.resolve(&self.root_path)?;
        }
        Ok(())
    }

    #[instrument(skip_all)]
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

    #[instrument(skip_all)]
    pub fn from_yaml_file(path: &Path) -> Result<Self, ServiceError> {
        Self::from_yaml(&std::fs::read_to_string(path).inspect_err(|e| {
            error!("Yaml error: {}", e);
        })?)
    }

    #[instrument(skip_all)]
    pub fn from_yaml(yaml_str: &str) -> Result<Self, ServiceError> {
        let mut spec: OpsmlServiceSpec = serde_yaml::from_str(yaml_str).inspect_err(|e| {
            error!("Failed to read yaml from string: {}", e);
        })?;
        spec.filter_deploy_by_environment()?;
        Ok(spec)
    }

    pub fn get_card(&self, alias: &str) -> Option<&CardVariant> {
        if let Some(service) = &self.service {
            if let Some(cards) = &service.cards {
                cards.iter().find(|card| card.alias() == alias)
            } else {
                None
            }
        } else {
            None
        }
    }

    fn validate(&mut self) -> Result<(), ServiceError> {
        self.validate_service_type()?;

        if let Some(service) = &mut self.service {
            service.validate(
                &self.root_path,
                self.space_config.get_space(),
                &self.service_type,
                &self.deploy,
            )?;
        }

        Ok(())
    }

    pub fn space(&self) -> &str {
        self.space_config.get_space()
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl OpsmlServiceSpec {
    #[new]
    pub fn new(
        name: String,
        space_config: SpaceConfig,
        service_type: ServiceType,
        metadata: Option<ServiceMetadata>,
        service: Option<ServiceConfig>,
        deploy: Option<Vec<DeploymentConfig>>,
    ) -> Result<Self, ServiceError> {
        let mut spec = OpsmlServiceSpec {
            name,
            space_config,
            service_type,
            metadata,
            service,
            deploy,
            root_path: PathBuf::new(),
        };
        spec.validate()?;
        Ok(spec)
    }

    #[staticmethod]
    #[pyo3(name = "from_path")]
    pub fn load_from_path(path: Option<PathBuf>) -> Result<Self, ServiceError> {
        let path = match path {
            Some(p) => p,
            None => {
                let current_dir = std::env::current_dir()?;
                current_dir.join(DEFAULT_SERVICE_FILENAME)
            }
        };

        let mut spec = Self::from_path(&path)?;
        spec.resolve()?;
        spec.validate()?;
        Ok(spec)
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    #[getter]
    #[pyo3(name = "space")]
    pub fn _py_space(&self) -> String {
        self.space_config.get_space().to_string()
    }
    #[getter]
    pub fn service_type(&self) -> ServiceType {
        self.service_type.clone()
    }
    #[getter]
    pub fn metadata(&self) -> Option<ServiceMetadata> {
        self.metadata.clone()
    }
    #[getter]
    pub fn service(&self) -> Option<ServiceConfig> {
        self.service.clone()
    }
    #[getter]
    pub fn deploy(&self) -> Option<Vec<DeploymentConfig>> {
        self.deploy.clone()
    }
    #[getter]
    pub fn root_path(&self) -> PathBuf {
        self.root_path.clone()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
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
    urls: [https://test.example.com]
    resources:
      cpu: 4
      memory: 16Gi
      storage: 100Gi
    links:
      logging: https://logging.example.com
"#;

        let spec = OpsmlServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");

        let model_card = spec.get_card("test_model").unwrap();
        assert_eq!(model_card.space(), "my-team");

        let prompt_card = spec.get_card("test_prompt").unwrap();
        assert_eq!(prompt_card.space(), "custom-space");
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
    urls: [https://test.example.com]
    resources:
      cpu: 4
      memory: 16Gi
      storage: 100Gi
    links:
      logging: https://logging.example.com
"#;

        let spec = OpsmlServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");
        assert_eq!(spec.service_type, ServiceType::Mcp);

        let service = spec.service.unwrap();
        let mcp_config = service.mcp.as_ref().unwrap();
        assert_eq!(mcp_config.transport, McpTransport::Http);

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
    urls: [https://test.example.com]
"#;

        let spec = OpsmlServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");
        assert_eq!(spec.service_type, ServiceType::Mcp);

        let service = spec.service.unwrap();
        let mcp_config = service.mcp.as_ref().unwrap();
        assert_eq!(mcp_config.transport, McpTransport::Http);

        assert!(mcp_config.capabilities.contains(&McpCapability::Resources));
        assert!(mcp_config.capabilities.contains(&McpCapability::Tools));
    }

    #[test]
    fn test_service_spec_with_prompt_card_path() {
        let yaml_content = r#"
name: test-service
team: my-team
type: Api
metadata:
  description: Test service with prompt card from path
  language: python
  tags: [ml, test]

service:
  version: "1.0.0"
  write_dir: "opsml_app/test_service"
  cards:
    - alias: my_prompt
      type: prompt
      path: "prompts/my_prompt.json"

deploy:
  - environment: development
"#;

        let spec = OpsmlServiceSpec::from_yaml(yaml_content).unwrap();
        assert_eq!(spec.name, "test-service");
        assert_eq!(spec.space(), "my-team");

        let prompt_card = spec.get_card("my_prompt").unwrap();
        assert_eq!(
            prompt_card.registry_type(),
            &opsml_types::RegistryType::Prompt
        );
        assert_eq!(
            prompt_card.path(),
            Some(PathBuf::from("prompts/my_prompt.json")).as_ref()
        );
    }
}
