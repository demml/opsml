use crate::RegistryType;
use crate::contracts::mcp::McpConfig;
use crate::contracts::{AgentSpec, SkillFormat};
use crate::error::{AgentConfigError, TypeError};
use opsml_semver::VersionType;
use opsml_utils::convert_keys_to_snake_case;
use opsml_utils::extract_py_attr;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use pyo3::types::PyDict;

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
pub struct CardPath {
    #[pyo3(get)]
    pub alias: String,
    #[serde(rename = "type")]
    #[pyo3(get)]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub drift: Option<DriftConfig>,
    #[pyo3(get)]
    pub path: PathBuf,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    #[pyo3(get)]
    pub version_type: Option<VersionType>,
}

impl CardPath {
    pub fn validate(&mut self, root_path: &Path) -> Result<(), TypeError> {
        // drift only supports model and prompt registry
        let has_drift = self.drift.is_some();
        let is_model_or_prompt =
            self.registry_type == RegistryType::Model || self.registry_type == RegistryType::Prompt;

        // Only allow drift configuration for model cards
        if has_drift && !is_model_or_prompt {
            return Err(TypeError::InvalidConfiguration);
        }

        // validate that the path exists and is a file
        let full_path = if self.path.is_absolute() {
            self.path.clone()
        } else {
            root_path.join(&self.path)
        };

        if !full_path.exists() {
            return Err(TypeError::PyError(format!(
                "Card file not found at path: {:?}",
                full_path
            )));
        }
        Ok(())
    }
}

/// Lock a service card by registering it if it doesn't have a uid, or validating it if it does
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
    pub version_type: Option<VersionType>,
}

#[pymethods]
impl Card {
    #[new]
    #[pyo3(signature = (alias, registry_type=None, space=None, name=None, version=None, uid=None, card=None, drift=None, version_type=None))]
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
        version_type: Option<VersionType>,
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
                version_type,
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
            version_type,
        })
    }
}

impl Card {
    #[allow(clippy::too_many_arguments)]
    pub fn rust_new(
        alias: String,
        registry_type: RegistryType,
        space: String,
        name: String,
        version: Option<String>,
        uid: Option<String>,
        drift: Option<DriftConfig>,
        version_type: Option<VersionType>,
    ) -> Card {
        Card {
            space,
            name,
            version,
            uid,
            registry_type,
            alias,
            drift,
            version_type,
        }
    }

    /// Validate the card configuration to ensure drift is only used for model cards
    pub fn validate(&mut self, service_space: &str) -> Result<(), TypeError> {
        // drift only supports model and prompt registry
        let has_drift = self.drift.is_some();
        let is_model_or_prompt =
            self.registry_type == RegistryType::Model || self.registry_type == RegistryType::Prompt;

        // Only allow drift configuration for model cards
        if has_drift && !is_model_or_prompt {
            return Err(TypeError::InvalidConfiguration);
        }

        if self.space.is_empty() {
            self.space = service_space.to_string();
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
pub enum CardVariant {
    Card(Card),
    Path(CardPath),
}

impl CardVariant {
    pub fn to_bound_py_any<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, TypeError> {
        match self {
            CardVariant::Card(args) => Ok(args.clone().into_bound_py_any(py)?),
            CardVariant::Path(path) => Ok(path.clone().into_bound_py_any(py)?),
        }
    }

    pub fn set_space(&mut self, service_space: &str) {
        if let CardVariant::Card(args) = self {
            args.set_space(service_space);
        }
    }

    pub fn validate(&mut self, service_space: &str, root_path: &Path) -> Result<(), TypeError> {
        match self {
            CardVariant::Card(args) => args.validate(service_space)?,
            CardVariant::Path(path) => path.validate(root_path)?,
        }
        Ok(())
    }

    pub fn alias(&self) -> &str {
        match self {
            CardVariant::Card(args) => &args.alias,
            CardVariant::Path(path) => &path.alias,
        }
    }

    pub fn space(&self) -> &str {
        match self {
            CardVariant::Card(args) => &args.space,
            CardVariant::Path(_) => "missing", // space is not available for path variant until we load the card content at runtime
        }
    }

    pub fn path(&self) -> Option<&PathBuf> {
        match self {
            CardVariant::Card(_) => None,
            CardVariant::Path(path) => Some(&path.path),
        }
    }

    pub fn registry_type(&self) -> &RegistryType {
        match self {
            CardVariant::Card(args) => &args.registry_type,
            CardVariant::Path(path) => &path.registry_type,
        }
    }

    pub fn drift(&self) -> Option<&DriftConfig> {
        match self {
            CardVariant::Card(args) => args.drift.as_ref(),
            CardVariant::Path(path) => path.drift.as_ref(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum AgentConfig {
    Spec(Box<AgentSpec>),
    Path(String),
}

impl AgentConfig {
    pub fn to_a2a_card<'py>(&self, py: Python<'py>) -> Result<(), AgentConfigError> {
        // import from a2a.types import AgentCard
        //let agent_card_type = py.import("a2a.types")?.getattr("AgentCard")?;
        match self {
            AgentConfig::Spec(spec) => {
                // filter skills for a2a enum variant
                let mut cloned_config = spec.clone();
                // mutate the skills to only include those with format A2A
                let filtered_skills: Vec<SkillFormat> = cloned_config
                    .skills
                    .iter()
                    .filter_map(|skill| {
                        match skill {
                            SkillFormat::A2A(_) => Some(skill.clone()),
                            SkillFormat::Standard(_) => None, // skip standard format skills
                        }
                    })
                    .collect::<Vec<_>>();

                cloned_config.skills = filtered_skills;

                // create py dict
                let camel_case_json = serde_json::to_value(cloned_config)?;
                let snake_case_json = convert_keys_to_snake_case(camel_case_json);
                let pythonized_config = pythonize::pythonize(py, &snake_case_json)?;

                //extrace to dict
                let agent_card_kwargs = pythonized_config.cast::<PyDict>()?;
                // iterate over skills
                // if skill key format is a2a then do nothing
                // if skill key format is standard, then remove that skill
                let agent_card = py.import("a2a.types")?.getattr("AgentCard")?;
                let _agent_card_instance = agent_card.call((), Some(agent_card_kwargs))?;

                Ok(())
            }
            AgentConfig::Path(_) => Err(AgentConfigError::InvalidAgentConfig),
        }
    }
    pub fn resolve(self, root_path: &Path) -> Result<Self, AgentConfigError> {
        match self {
            AgentConfig::Spec(spec) => Ok(AgentConfig::Spec(spec)),
            AgentConfig::Path(path) => {
                let agent_path = if Path::new(&path).is_absolute() {
                    PathBuf::from(path)
                } else {
                    root_path.join(path)
                };

                let content = std::fs::read_to_string(&agent_path).inspect_err(|e| {
                    error!("Failed to read agent spec file at {:?}: {}", agent_path, e);
                })?;
                Ok(serde_yaml::from_str(&content)?)
            }
        }
    }

    /// This will perform conversion of String path to AgentSpec and validate AgentSpec if provided as path. If AgentSpec is already provided, it will just validate it.
    pub fn validate(&self, root_path: &Path) -> Result<(), AgentConfigError> {
        // validates the agent configuration
        match self {
            AgentConfig::Spec(spec) => {
                spec.validate(root_path)?;
                Ok(())
            }
            AgentConfig::Path(_) => Err(AgentConfigError::InvalidAgentConfig), // Path should have been resolved at this point
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[pyclass]
pub struct ServiceConfig {
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cards: Option<Vec<CardVariant>>,
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub write_dir: Option<String>,
    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mcp: Option<McpConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agent: Option<AgentConfig>,
}

impl ServiceConfig {
    pub fn validate(
        &mut self,
        root_path: &Path,
        service_space: &str,
        service_type: &ServiceType,
    ) -> Result<(), TypeError> {
        // validate cards and set space if not provided
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate(service_space, root_path)?;
            }
        }

        // MCP services must have MCP config
        if service_type == &ServiceType::Mcp && self.mcp.is_none() {
            return Err(TypeError::MissingMCPConfig);
        }

        // Agent services must have agent config
        if service_type == &ServiceType::Agent && self.agent.is_none() {
            return Err(AgentConfigError::MissingAgentConfig.into());
        }

        // Validate agent config if present
        if let Some(agent_config) = &self.agent {
            // currently validates:
            // 1. Agent Skills (if provided)
            agent_config.validate(root_path)?;
        }
        Ok(())
    }

    pub fn resolve(&mut self, root_path: &Path) -> Result<(), AgentConfigError> {
        // resolve agent config if it's a path
        if let Some(agent_config) = self.agent.take() {
            self.agent = Some(agent_config.resolve(root_path)?);
        }
        Ok(())
    }
}

#[pymethods]
impl ServiceConfig {
    #[new]
    pub fn new(
        version: Option<String>,
        cards: Option<Vec<Bound<'_, PyAny>>>,
        write_dir: Option<String>,
        mcp: Option<McpConfig>,
        agent: Option<AgentSpec>,
    ) -> Result<Self, TypeError> {
        let agent_config = agent.map(|spec| AgentConfig::Spec(Box::new(spec)));

        // iterate over cards and convert to CardVariant
        let cards = if let Some(cards) = cards {
            let mut card_variants = Vec::new();
            for card in cards {
                if card.is_instance_of::<Card>() {
                    let card_args = card.extract::<Card>()?;
                    card_variants.push(CardVariant::Card(card_args));
                } else if card.is_instance_of::<CardPath>() {
                    let card_path = card.extract::<CardPath>()?;
                    card_variants.push(CardVariant::Path(card_path));
                } else {
                    error!("Invalid card type: {:?}", card);
                    return Err(TypeError::InvalidCardType);
                }
            }
            Some(card_variants)
        } else {
            None
        };

        Ok(ServiceConfig {
            version,
            cards,
            write_dir,
            mcp,
            agent: agent_config,
        })
    }

    #[getter]
    pub fn get_cards<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Option<Vec<Bound<'py, PyAny>>>, TypeError> {
        if let Some(cards) = &self.cards {
            let mut py_cards = Vec::new();
            for card in cards {
                py_cards.push(card.to_bound_py_any(py)?);
            }
            return Ok(Some(py_cards));
        }

        Ok(None)
    }
}
