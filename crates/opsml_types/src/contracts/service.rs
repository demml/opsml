use crate::contracts::mcp::McpConfig;
use crate::contracts::AgentSpec;
use crate::error::TypeError;
use crate::RegistryType;
use opsml_utils::extract_py_attr;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;
use std::path::{Path, PathBuf};
use tracing::error;
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Default)]
#[pyclass(eq, eq_int)]
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
impl From<String> for ServiceType {
    fn from(s: String) -> Self {
        match s.to_lowercase().as_str() {
            "api" => ServiceType::Api,
            "mcp" => ServiceType::Mcp,
            "agent" => ServiceType::Agent,
            _ => ServiceType::Api, // default to Api if unknown
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

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[pyclass]
pub struct ServiceMetadata {
    #[pyo3(get)]
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub language: Option<String>,
    #[pyo3(get)]
    pub tags: Vec<String>,
}

#[pymethods]
impl ServiceMetadata {
    #[new]
    pub fn new(description: String, language: Option<String>, tags: Option<Vec<String>>) -> Self {
        ServiceMetadata {
            description,
            language,
            tags: tags.unwrap_or_default(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct GpuConfig {
    #[serde(rename = "type")]
    #[pyo3(get)]
    pub gpu_type: String,
    #[pyo3(get)]
    pub count: u32,
    #[pyo3(get)]
    pub memory: String,
}

#[pymethods]
impl GpuConfig {
    #[new]
    pub fn new(gpu_type: String, count: u32, memory: String) -> Self {
        GpuConfig {
            gpu_type,
            count,
            memory,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct Resources {
    #[pyo3(get)]
    pub cpu: u32,
    #[pyo3(get)]
    pub memory: String,
    #[pyo3(get)]
    pub storage: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub gpu: Option<GpuConfig>,
}

#[pymethods]
impl Resources {
    #[new]
    pub fn new(cpu: u32, memory: String, storage: String, gpu: Option<GpuConfig>) -> Self {
        Resources {
            cpu,
            memory,
            storage,
            gpu,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct DeploymentConfig {
    #[pyo3(get)]
    pub environment: String,
    #[pyo3(get)]
    pub provider: Option<String>,
    #[pyo3(get)]
    pub location: Option<Vec<String>>,
    #[pyo3(get)]
    pub endpoints: Vec<String>,
    #[pyo3(get)]
    pub resources: Option<Resources>,
    #[pyo3(get)]
    pub links: Option<HashMap<String, String>>,
}
#[pymethods]
impl DeploymentConfig {
    #[new]
    #[pyo3(signature = (environment, provider=None, location=None, endpoints=None, resources=None, links=None))]
    pub fn new(
        environment: String,
        provider: Option<String>,
        location: Option<Vec<String>>,
        endpoints: Option<Vec<String>>,
        resources: Option<Resources>,
        links: Option<HashMap<String, String>>,
    ) -> Self {
        DeploymentConfig {
            environment,
            provider,
            location,
            endpoints: endpoints.unwrap_or_default(),
            resources,
            links,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default, PartialEq)]
#[pyclass(eq)]
pub struct DriftConfig {
    #[serde(default)]
    #[pyo3(get)]
    pub active: bool,
    #[serde(default)]
    #[pyo3(get)]
    pub deactivate_others: bool,
    #[pyo3(get)]
    pub drift_type: Vec<String>,
}

#[pymethods]
impl DriftConfig {
    #[new]
    pub fn new(active: bool, deactivate_others: bool, drift_type: Vec<String>) -> Self {
        DriftConfig {
            active,
            deactivate_others,
            drift_type,
        }
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Card {
    #[pyo3(get)]
    pub alias: String,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    #[pyo3(get)]
    pub space: String,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub version: Option<String>,
    #[serde(rename = "type")]
    #[pyo3(get)]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub drift: Option<DriftConfig>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub uid: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub path: Option<String>,
}

#[pymethods]
impl Card {
    #[new]
    #[pyo3(signature = (alias, registry_type=None, space=None, name=None, version=None, uid=None, card=None, drift=None, path=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        alias: String,
        registry_type: Option<RegistryType>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        card: Option<Bound<'_, PyAny>>,
        drift: Option<DriftConfig>,
        path: Option<&str>,
    ) -> Result<Self, TypeError> {
        // If card object is provided, extract all attributes from it
        if let Some(card) = card {
            let registry_type = extract_py_attr::<RegistryType>(&card, "registry_type")?;

            let uid = extract_py_attr::<Option<String>>(&card, "uid")?;

            let name = extract_py_attr::<String>(&card, "name")?;

            let space = extract_py_attr::<String>(&card, "space")?;

            let version = extract_py_attr::<String>(&card, "version")?;

            return Ok(Card {
                space,
                name,
                version: Some(version),
                uid,
                registry_type,
                alias,
                drift,
                path: None,
            });
        }

        let registry_type = match registry_type {
            Some(registry_type) => registry_type,
            None => {
                error!("Registry type is required unless a registered card is provided");
                return Err(TypeError::MissingRegistryTypeError);
            }
        };

        // Validate that either (space AND name) OR uid is provided
        let has_space_and_name = space.is_some() && name.is_some();
        let has_uid = uid.is_some();

        if !has_space_and_name && !has_uid {
            error!("Either both space and name, or uid must be provided");
            return Err(TypeError::MissingServiceCardArgsError);
        }

        Ok(Card {
            space: space.map(String::from).unwrap_or_default(),
            name: name.map(String::from).unwrap_or_default(),
            version: version.map(String::from),
            uid: uid.map(String::from),
            registry_type,
            alias,
            drift,
            path: path.map(String::from),
        })
    }
}

impl Card {
    pub fn rust_new(
        alias: String,
        registry_type: RegistryType,
        space: String,
        name: String,
        version: Option<String>,
        uid: Option<String>,
        drift: Option<DriftConfig>,
    ) -> Card {
        Card {
            space,
            name,
            version,
            uid,
            registry_type,
            alias,
            drift,
            path: None,
        }
    }

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

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum AgentConfig {
    Path(String),
    Spec(Box<AgentSpec>),
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[pyclass]
pub struct ServiceConfig {
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cards: Option<Vec<Card>>,
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub write_dir: Option<String>,
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mcp: Option<McpConfig>,

    #[serde(skip)]
    pub agent_config: Option<AgentConfig>,

    #[serde(skip)]
    #[pyo3(get)]
    pub agent: Option<AgentSpec>,
}

impl ServiceConfig {
    pub fn load_agent_spec(&mut self, root_path: &Path) -> Result<(), TypeError> {
        if let Some(agent_config) = &self.agent_config {
            match agent_config {
                AgentConfig::Path(path) => {
                    let agent_path = if Path::new(path).is_absolute() {
                        PathBuf::from(path)
                    } else {
                        root_path.join(path)
                    };

                    let content = std::fs::read_to_string(&agent_path)?;
                    let spec: AgentSpec = serde_json::from_str(&content)?;
                    self.agent = Some(spec);
                }
                AgentConfig::Spec(spec) => {
                    self.agent = Some((**spec).clone());
                }
            }
        }
        Ok(())
    }
    pub fn validate(
        &mut self,
        service_space: &str,
        service_type: &ServiceType,
        root_path: Option<&Path>,
    ) -> Result<(), TypeError> {
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate()?;
                card.set_space(service_space);
            }
        }

        if service_type == &ServiceType::Mcp && self.mcp.is_none() {
            return Err(TypeError::MissingMCPConfig);
        }

        if service_type == &ServiceType::Agent {
            if let Some(root) = root_path {
                self.load_agent_spec(root)?;
            }

            if self.agent.is_none() {
                return Err(TypeError::MissingAgentConfig);
            }
        }

        Ok(())
    }
}

#[pymethods]
impl ServiceConfig {
    #[new]
    pub fn new(
        version: Option<String>,
        cards: Option<Vec<Card>>,
        write_dir: Option<String>,
        mcp: Option<McpConfig>,
        agent: Option<AgentSpec>,
    ) -> Result<Self, TypeError> {
        Ok(ServiceConfig {
            version,
            cards,
            write_dir,
            mcp,
            agent_config: None,
            agent,
        })
    }
}
