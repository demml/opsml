use crate::RegistryType;
use crate::contracts::AgentSpec;
use crate::contracts::mcp::McpConfig;
use crate::contracts::potato::PotatoAgentConfig;
use crate::contracts::workflow::WorkflowSpec;
use crate::error::{AgentConfigError, TypeError};
use opsml_semver::VersionType;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;
use std::path::{Path, PathBuf};
use tracing::error;

#[cfg(feature = "python")]
use opsml_utils::extract_py_attr;
#[cfg(feature = "python")]
use pyo3::IntoPyObjectExt;
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Default)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
pub enum ServiceType {
    #[default]
    #[serde(alias = "API", alias = "api")]
    Api,
    #[serde(alias = "MCP", alias = "mcp")]
    Mcp,
    #[serde(alias = "AGENT", alias = "agent")]
    Agent,
    #[serde(alias = "WORKFLOW", alias = "workflow")]
    Workflow,
}

impl Display for ServiceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ServiceType::Api => write!(f, "Api"),
            ServiceType::Mcp => write!(f, "Mcp"),
            ServiceType::Agent => write!(f, "Agent"),
            ServiceType::Workflow => write!(f, "Workflow"),
        }
    }
}

impl From<String> for ServiceType {
    fn from(s: String) -> Self {
        match s.to_lowercase().as_str() {
            "api" => ServiceType::Api,
            "mcp" => ServiceType::Mcp,
            "agent" => ServiceType::Agent,
            "workflow" => ServiceType::Workflow,
            _ => ServiceType::Api,
        }
    }
}

impl From<&str> for ServiceType {
    fn from(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "api" => ServiceType::Api,
            "mcp" => ServiceType::Mcp,
            "agent" => ServiceType::Agent,
            "workflow" => ServiceType::Workflow,
            _ => ServiceType::Api,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct ServiceMetadata {
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
    pub tags: Vec<String>,
}

impl ServiceMetadata {
    pub fn new(description: String, language: Option<String>, tags: Option<Vec<String>>) -> Self {
        ServiceMetadata {
            description,
            language,
            tags: tags.unwrap_or_default(),
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl ServiceMetadata {
    #[new]
    pub fn py_new(
        description: String,
        language: Option<String>,
        tags: Option<Vec<String>>,
    ) -> Self {
        Self::new(description, language, tags)
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[getter]
    pub fn language(&self) -> Option<String> {
        self.language.clone()
    }

    #[getter]
    pub fn tags(&self) -> Vec<String> {
        self.tags.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct GpuConfig {
    #[serde(rename = "type")]
    pub gpu_type: String,
    pub count: u32,
    pub memory: String,
}

impl GpuConfig {
    pub fn new(gpu_type: String, count: u32, memory: String) -> Self {
        GpuConfig {
            gpu_type,
            count,
            memory,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl GpuConfig {
    #[new]
    pub fn py_new(gpu_type: String, count: u32, memory: String) -> Self {
        Self::new(gpu_type, count, memory)
    }

    #[getter]
    pub fn gpu_type(&self) -> String {
        self.gpu_type.clone()
    }

    #[getter]
    pub fn count(&self) -> u32 {
        self.count
    }

    #[getter]
    pub fn memory(&self) -> String {
        self.memory.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct Resources {
    pub cpu: u32,
    pub memory: String,
    pub storage: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gpu: Option<GpuConfig>,
}

impl Resources {
    pub fn new(cpu: u32, memory: String, storage: String, gpu: Option<GpuConfig>) -> Self {
        Resources {
            cpu,
            memory,
            storage,
            gpu,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl Resources {
    #[new]
    pub fn py_new(cpu: u32, memory: String, storage: String, gpu: Option<GpuConfig>) -> Self {
        Self::new(cpu, memory, storage, gpu)
    }

    #[getter]
    pub fn cpu(&self) -> u32 {
        self.cpu
    }

    #[getter]
    pub fn memory(&self) -> String {
        self.memory.clone()
    }

    #[getter]
    pub fn storage(&self) -> String {
        self.storage.clone()
    }

    #[getter]
    pub fn gpu(&self) -> Option<GpuConfig> {
        self.gpu.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct DeploymentConfig {
    /// The environment this deployment config applies to (e.g. "production", "staging", "dev")
    pub environment: String,

    /// The provider to deploy to (e.g. "aws", "gcp", "azure", "local")
    pub provider: Option<String>,

    /// The location/region to deploy to (e.g. ["us-east-1", "us-west-2"] for AWS)
    pub location: Option<Vec<String>>,

    /// Base URLs where the service is deployed and accessible
    /// Example: ["https://api.example.com", "https://api.example.com/v2"]
    #[serde(alias = "endpoints")]
    pub urls: Vec<String>,

    /// The resource requirements for this deployment config
    pub resources: Option<Resources>,

    /// Additional links related to this deployment (e.g. monitoring dashboard, logs, etc.)
    pub links: Option<HashMap<String, String>>,

    /// Health check endpoint path (relative to base URL)
    /// Example: "/health" or "/api/v1/health"
    pub healthcheck: Option<String>,
}

impl DeploymentConfig {
    pub fn new(
        environment: String,
        provider: Option<String>,
        location: Option<Vec<String>>,
        urls: Option<Vec<String>>,
        resources: Option<Resources>,
        links: Option<HashMap<String, String>>,
        healthcheck: Option<String>,
    ) -> Self {
        DeploymentConfig {
            environment,
            provider,
            location,
            urls: urls.unwrap_or_default(),
            resources,
            links,
            healthcheck,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl DeploymentConfig {
    #[new]
    #[pyo3(signature = (environment, provider=None, location=None, urls=None, resources=None, links=None, healthcheck=None))]
    pub fn py_new(
        environment: String,
        provider: Option<String>,
        location: Option<Vec<String>>,
        urls: Option<Vec<String>>,
        resources: Option<Resources>,
        links: Option<HashMap<String, String>>,
        healthcheck: Option<String>,
    ) -> Self {
        Self::new(
            environment,
            provider,
            location,
            urls,
            resources,
            links,
            healthcheck,
        )
    }

    #[getter]
    pub fn environment(&self) -> String {
        self.environment.clone()
    }

    #[getter]
    pub fn provider(&self) -> Option<String> {
        self.provider.clone()
    }

    #[getter]
    pub fn location(&self) -> Option<Vec<String>> {
        self.location.clone()
    }

    #[getter]
    pub fn urls(&self) -> Vec<String> {
        self.urls.clone()
    }

    #[getter]
    pub fn resources(&self) -> Option<Resources> {
        self.resources.clone()
    }

    #[getter]
    pub fn links(&self) -> Option<HashMap<String, String>> {
        self.links.clone()
    }

    #[getter]
    pub fn healthcheck(&self) -> Option<String> {
        self.healthcheck.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default, PartialEq)]
#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
pub struct DriftConfig {
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub deactivate_others: bool,
    pub drift_type: Vec<String>,
}

impl DriftConfig {
    pub fn new(active: bool, deactivate_others: bool, drift_type: Vec<String>) -> Self {
        DriftConfig {
            active,
            deactivate_others,
            drift_type,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl DriftConfig {
    #[new]
    pub fn py_new(active: bool, deactivate_others: bool, drift_type: Vec<String>) -> Self {
        Self::new(active, deactivate_others, drift_type)
    }

    #[getter]
    pub fn active(&self) -> bool {
        self.active
    }

    #[getter]
    pub fn deactivate_others(&self) -> bool {
        self.deactivate_others
    }

    #[getter]
    pub fn drift_type(&self) -> Vec<String> {
        self.drift_type.clone()
    }
}

#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct CardPath {
    pub alias: String,
    #[serde(alias = "type")]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift: Option<DriftConfig>,
    pub path: PathBuf,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_type: Option<VersionType>,
}

impl CardPath {
    pub fn validate(&mut self, root_path: &Path) -> Result<(), TypeError> {
        let has_drift = self.drift.is_some();
        let is_model_or_prompt =
            self.registry_type == RegistryType::Model || self.registry_type == RegistryType::Prompt;

        if has_drift && !is_model_or_prompt {
            return Err(TypeError::InvalidConfiguration);
        }

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

#[cfg(feature = "python")]
#[pymethods]
impl CardPath {
    #[getter]
    pub fn alias(&self) -> String {
        self.alias.clone()
    }

    #[getter]
    pub fn registry_type(&self) -> RegistryType {
        self.registry_type.clone()
    }

    #[getter]
    pub fn drift(&self) -> Option<DriftConfig> {
        self.drift.clone()
    }

    #[getter]
    pub fn path(&self) -> PathBuf {
        self.path.clone()
    }

    #[getter]
    pub fn version_type(&self) -> Option<VersionType> {
        self.version_type.clone()
    }
}

mod version_deserializer {
    use serde::{Deserialize, Deserializer};

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(untagged)]
        enum StringOrInt {
            String(String),
            Int(i64),
        }

        Ok(
            Option::<StringOrInt>::deserialize(deserializer)?.map(|v| match v {
                StringOrInt::String(s) => s,
                StringOrInt::Int(i) => i.to_string(),
            }),
        )
    }
}

/// Lock a service card by registering it if it doesn't have a uid, or validating it if it does
#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Card {
    pub alias: String,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub space: String,
    pub name: String,
    #[serde(default, deserialize_with = "version_deserializer::deserialize")]
    pub version: Option<String>,
    #[serde(alias = "type")]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift: Option<DriftConfig>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub uid: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_type: Option<VersionType>,
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
        let has_drift = self.drift.is_some();
        let is_model_or_prompt =
            self.registry_type == RegistryType::Model || self.registry_type == RegistryType::Prompt;

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

#[cfg(feature = "python")]
#[pymethods]
impl Card {
    #[new]
    #[pyo3(signature = (alias, registry_type=None, space=None, name=None, version=None, uid=None, card=None, drift=None, version_type=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn py_new(
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

    #[getter]
    pub fn alias(&self) -> String {
        self.alias.clone()
    }

    #[getter]
    pub fn space(&self) -> String {
        self.space.clone()
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[getter]
    pub fn version(&self) -> Option<String> {
        self.version.clone()
    }

    #[getter]
    pub fn registry_type(&self) -> RegistryType {
        self.registry_type.clone()
    }

    #[getter]
    pub fn drift(&self) -> Option<DriftConfig> {
        self.drift.clone()
    }

    #[getter]
    pub fn uid(&self) -> Option<String> {
        self.uid.clone()
    }

    #[getter]
    pub fn version_type(&self) -> Option<VersionType> {
        self.version_type.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum CardVariant {
    Card(Card),
    Path(CardPath),
}

impl CardVariant {
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
            CardVariant::Path(_) => "missing",
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

#[cfg(feature = "python")]
impl CardVariant {
    pub fn to_bound_py_any<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, TypeError> {
        match self {
            CardVariant::Card(args) => Ok(args.clone().into_bound_py_any(py)?),
            CardVariant::Path(path) => Ok(path.clone().into_bound_py_any(py)?),
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
    pub fn validate(
        &mut self,
        root_path: &Path,
        deploy_config: &Option<Vec<DeploymentConfig>>,
    ) -> Result<(), AgentConfigError> {
        match self {
            AgentConfig::Spec(spec) => {
                spec.validate(root_path, deploy_config)?;
                Ok(())
            }
            AgentConfig::Path(_) => Err(AgentConfigError::InvalidAgentConfig),
        }
    }
}

#[cfg(feature = "python")]
impl AgentConfig {
    pub fn to_a2a_card<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, AgentSpec>, AgentConfigError> {
        match self {
            AgentConfig::Spec(spec) => {
                let agent_card = Py::new(py, spec.as_ref().clone())?;
                let bound_card = agent_card.bind(py).clone();
                Ok(bound_card)
            }
            AgentConfig::Path(_) => Err(AgentConfigError::InvalidAgentConfig),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct ServiceConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cards: Option<Vec<CardVariant>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub write_dir: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mcp: Option<McpConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agent: Option<AgentConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub potato: Option<PotatoAgentConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub workflow: Option<WorkflowSpec>,
}

impl ServiceConfig {
    pub fn validate(
        &mut self,
        root_path: &Path,
        service_space: &str,
        service_type: &ServiceType,
        deployment_config: &Option<Vec<DeploymentConfig>>,
    ) -> Result<(), TypeError> {
        if let Some(cards) = &mut self.cards {
            for card in cards {
                card.validate(service_space, root_path)?;
            }
        }

        if service_type == &ServiceType::Mcp && self.mcp.is_none() {
            return Err(TypeError::MissingMCPConfig);
        }

        if service_type == &ServiceType::Agent && self.agent.is_none() {
            return Err(AgentConfigError::MissingAgentConfig.into());
        }

        if let Some(agent_config) = &mut self.agent {
            agent_config.validate(root_path, deployment_config)?;
        }

        if service_type == &ServiceType::Workflow {
            if let Some(wf) = &self.workflow {
                wf.validate()?;
            } else {
                return Err(TypeError::WorkflowValidation(
                    "Workflow service type requires 'workflow' configuration".into(),
                ));
            }
        }

        Ok(())
    }

    pub fn resolve(&mut self, root_path: &Path) -> Result<(), AgentConfigError> {
        if let Some(agent_config) = self.agent.take() {
            self.agent = Some(agent_config.resolve(root_path)?);
        }
        Ok(())
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl ServiceConfig {
    #[new]
    pub fn py_new(
        version: Option<String>,
        cards: Option<Vec<Bound<'_, PyAny>>>,
        write_dir: Option<String>,
        mcp: Option<McpConfig>,
        agent: Option<AgentSpec>,
    ) -> Result<Self, TypeError> {
        let agent_config = agent.map(|spec| AgentConfig::Spec(Box::new(spec)));

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
            potato: None,
            workflow: None,
        })
    }

    #[getter]
    pub fn version(&self) -> Option<String> {
        self.version.clone()
    }

    #[getter]
    pub fn write_dir(&self) -> Option<String> {
        self.write_dir.clone()
    }

    #[getter]
    pub fn mcp(&self) -> Option<McpConfig> {
        self.mcp.clone()
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contracts::workflow::{CardRef, WorkflowStep};

    fn skill_step(name: &str) -> WorkflowStep {
        WorkflowStep {
            name: name.into(),
            skill: Some(CardRef {
                space: "platform".into(),
                name: "my-skill".into(),
                version: None,
            }),
            ..Default::default()
        }
    }

    #[test]
    fn test_service_config_workflow_missing_config_returns_err() {
        let mut config = ServiceConfig::default();
        let err = config
            .validate(
                std::path::Path::new("."),
                "test",
                &ServiceType::Workflow,
                &None,
            )
            .unwrap_err();
        assert!(
            err.to_string().contains("workflow") || err.to_string().contains("Workflow"),
            "unexpected error: {err}"
        );
    }

    #[test]
    fn test_service_config_workflow_invalid_dag_propagates_err() {
        // Cycle: s1 → s2 → s1
        let mut s1 = skill_step("s1");
        s1.depends_on = vec!["s2".into()];
        let mut s2 = skill_step("s2");
        s2.depends_on = vec!["s1".into()];

        let mut config = ServiceConfig {
            workflow: Some(WorkflowSpec {
                steps: vec![s1, s2],
                ..Default::default()
            }),
            ..Default::default()
        };
        let err = config
            .validate(
                std::path::Path::new("."),
                "test",
                &ServiceType::Workflow,
                &None,
            )
            .unwrap_err();
        assert!(
            err.to_string().contains("cycle"),
            "expected cycle error, got: {err}"
        );
    }

    #[test]
    fn test_service_config_workflow_valid_linear_dag_is_ok() {
        let s1 = skill_step("s1");
        let mut s2 = skill_step("s2");
        s2.depends_on = vec!["s1".into()];

        let mut config = ServiceConfig {
            workflow: Some(WorkflowSpec {
                steps: vec![s1, s2],
                ..Default::default()
            }),
            ..Default::default()
        };
        assert!(
            config
                .validate(
                    std::path::Path::new("."),
                    "test",
                    &ServiceType::Workflow,
                    &None,
                )
                .is_ok()
        );
    }
}
