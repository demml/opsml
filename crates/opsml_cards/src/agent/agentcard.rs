use crate::error::CardError;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_types::contracts::{AgentCardClientRecord, CardRecord};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use pyo3::prelude::*;
use pythonize::depythonize;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, error};
// ============================================================================
// A2A Protocol Data Structures
// ============================================================================

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentProvider {
    #[pyo3(get, set)]
    pub organization: String,

    #[pyo3(get, set)]
    pub url: String,
}

#[pymethods]
impl AgentProvider {
    #[new]
    pub fn new(organization: Option<String>, url: Option<String>) -> Self {
        Self {
            organization: organization.unwrap_or_default(),
            url: url.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentInterface {
    #[pyo3(get, set)]
    pub url: String,

    #[pyo3(get, set)]
    pub protocol_binding: String,

    #[pyo3(get, set)]
    pub protocol_version: String,

    #[pyo3(get, set)]
    pub tenant: String,
}

#[pymethods]
impl AgentInterface {
    #[new]
    #[pyo3(signature = (url, protocol_binding, protocol_version, tenant=None))]
    pub fn new(
        url: String,
        protocol_binding: String,
        protocol_version: String,
        tenant: Option<String>,
    ) -> Self {
        Self {
            url,
            protocol_binding,
            protocol_version,
            tenant: tenant.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentExtension {
    #[pyo3(get, set)]
    pub description: Option<String>,

    pub params: Option<Value>,

    #[pyo3(get, set)]
    pub required: bool,

    #[pyo3(get, set)]
    pub uri: String,
}

#[pymethods]
impl AgentExtension {
    #[new]
    #[pyo3(signature = (uri, description=None, params=None, required=false))]
    pub fn new(
        uri: String,
        description: Option<String>,
        params: Option<&Bound<'_, PyAny>>,
        required: bool,
    ) -> Self {
        let depythonized = match params {
            Some(p) => Some(depythonize(p).unwrap_or_default()),
            None => None,
        };
        Self {
            uri,
            description,
            params: depythonized,
            required,
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentCapabilities {
    #[pyo3(get, set)]
    pub streaming: bool,

    #[pyo3(get, set)]
    pub push_notifications: bool,

    #[pyo3(get, set)]
    pub extended_agent_card: bool,

    #[pyo3(get, set)]
    pub extensions: Vec<AgentExtension>,
}

#[pymethods]
impl AgentCapabilities {
    #[new]
    #[pyo3(signature = (streaming=false, push_notifications=false, extended_agent_card=false, extensions=None))]
    pub fn new(
        streaming: bool,
        push_notifications: bool,
        extended_agent_card: bool,
        extensions: Option<Vec<AgentExtension>>,
    ) -> Self {
        Self {
            streaming,
            push_notifications,
            extended_agent_card,
            extensions: extensions.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct SecurityRequirement {
    #[pyo3(get, set)]
    pub schemes: Vec<String>,
}

#[pymethods]
impl SecurityRequirement {
    #[new]
    pub fn new(schemes: Vec<String>) -> Self {
        Self { schemes }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentSkill {
    #[pyo3(get, set)]
    pub description: String,

    #[pyo3(get, set)]
    pub examples: Vec<String>,

    #[pyo3(get, set)]
    pub id: String,

    #[pyo3(get, set)]
    pub input_modes: Option<Vec<String>>,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub output_modes: Option<Vec<String>>,

    #[pyo3(get, set)]
    pub security_requirements: Option<Vec<SecurityRequirement>>,

    #[pyo3(get, set)]
    pub tags: Vec<String>,
}

#[pymethods]
impl AgentSkill {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (id, name, description, tags=None, examples=None, input_modes=None, output_modes=None, security_requirements=None))]
    pub fn new(
        id: String,
        name: String,
        description: String,
        tags: Option<Vec<String>>,
        examples: Option<Vec<String>>,
        input_modes: Option<Vec<String>>,
        output_modes: Option<Vec<String>>,
        security_requirements: Option<Vec<SecurityRequirement>>,
    ) -> Self {
        Self {
            id,
            name,
            description,
            tags: tags.unwrap_or_default(),
            examples: examples.unwrap_or_default(),
            input_modes,
            output_modes,
            security_requirements,
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ApiKeySecurityScheme {
    pub description: Option<String>,
    pub location: String,
    pub name: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct HttpAuthSecurityScheme {
    scheme: String,
    bearer_format: String,
    description: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct MtlsSecurityScheme {
    description: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct Oauth2SecurityScheme {
    pub description: Option<String>,
    pub flows: OAuthFlows,
    pub oauth2_metadata_url: Option<String>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OpenIdConnectSecurityScheme {
    pub description: Option<String>,
    pub open_id_connect_url: Option<String>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum SecurityScheme {
    ApiKeySecurityScheme(ApiKeySecurityScheme),
    HttpAuthSecurityScheme(HttpAuthSecurityScheme),
    MtlsSecurityScheme(MtlsSecurityScheme),
    Oauth2SecurityScheme(Oauth2SecurityScheme),
    OpenIdConnectSecurityScheme(OpenIdConnectSecurityScheme),
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OAuthFlows {
    pub authorization_code: Option<AuthorizationCodeFlow>,
    pub client_credentials: Option<ClientCredentialsFlow>,
    pub device_code: Option<DeviceCodeFlow>,
    pub implicit: Option<ImplicitAuthFlow>,
    pub password: Option<PassWordAuthFlow>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AuthorizationCodeFlow {
    pub authorization_url: String,
    pub pkce_required: bool,
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    pub token_url: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ClientCredentialsFlow {
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    pub token_url: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct DeviceCodeFlow {
    pub device_authorization_url: String,
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    pub token_url: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ImplicitAuthFlow {
    pub authorization_url: String,
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PassWordAuthFlow {
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    pub token_url: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentCardSignature {
    pub header: Option<HashMap<String, String>>,
    pub protected: String,
    pub signature: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentSpec {
    #[pyo3(get, set)]
    pub capabilities: AgentCapabilities,

    #[pyo3(get, set)]
    pub default_output_modes: Vec<String>,

    #[pyo3(get, set)]
    pub default_input_modes: Vec<String>,

    #[pyo3(get, set)]
    pub description: String,

    #[pyo3(get, set)]
    pub documentation_url: Option<String>,

    #[pyo3(get, set)]
    pub icon_url: Option<String>,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub provider: Option<AgentProvider>,

    #[pyo3(get, set)]
    pub security_requirements: Option<Vec<SecurityRequirement>>,

    #[pyo3(get, set)]
    pub security_schemes: Option<HashMap<String, SecurityScheme>>,

    #[pyo3(get, set)]
    pub signatures: Option<Vec<AgentCardSignature>>,

    #[pyo3(get, set)]
    pub skills: Vec<AgentSkill>,

    #[pyo3(get, set)]
    pub supported_interfaces: Vec<AgentInterface>,

    #[pyo3(get, set)]
    pub version: String,
}

#[pymethods]
impl AgentSpec {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (
        name,
        description,
        version,
        supported_interfaces,
        capabilities,
        default_input_modes,
        default_output_modes,
        skills,
        provider=None,
        documentation_url=None,
        icon_url=None,
        security_schemes=None,
        security_requirements=None,
        signatures=None
    ))]
    pub fn new(
        name: String,
        description: String,
        version: String,
        supported_interfaces: Vec<AgentInterface>,
        capabilities: AgentCapabilities,
        default_input_modes: Vec<String>,
        default_output_modes: Vec<String>,
        skills: Vec<AgentSkill>,
        provider: Option<AgentProvider>,
        documentation_url: Option<String>,
        icon_url: Option<String>,
        security_schemes: Option<HashMap<String, SecurityScheme>>,
        security_requirements: Option<Vec<SecurityRequirement>>,
        signatures: Option<Vec<AgentCardSignature>>,
    ) -> Self {
        Self {
            name,
            description,
            version,
            supported_interfaces,
            provider,
            documentation_url,
            icon_url,
            capabilities,
            default_input_modes,
            default_output_modes,
            skills,
            security_schemes,
            security_requirements,
            signatures,
        }
    }
}

// ============================================================================
// Task and Message Types (for runtime execution tracking)
// ============================================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TaskState {
    TaskStateUnspecified,
    TaskStateSubmitted,
    TaskStateWorking,
    TaskStateCompleted,
    TaskStateFailed,
    TaskStateCanceled,
    TaskStateInputRequired,
    TaskStateRejected,
    TaskStateAuthRequired,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Role {
    RoleUnspecified,
    RoleUser,
    RoleAgent,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum Part {
    Text {
        text: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        metadata: Option<HashMap<String, serde_json::Value>>,
        #[serde(skip_serializing_if = "Option::is_none")]
        media_type: Option<String>,
    },
    File {
        #[serde(skip_serializing_if = "Option::is_none")]
        raw: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        url: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        filename: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        media_type: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        metadata: Option<HashMap<String, serde_json::Value>>,
    },
    Data {
        data: serde_json::Value,
        #[serde(skip_serializing_if = "Option::is_none")]
        metadata: Option<HashMap<String, serde_json::Value>>,
        #[serde(skip_serializing_if = "Option::is_none")]
        media_type: Option<String>,
    },
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Message {
    pub message_id: String,
    pub role: Role,
    pub parts: Vec<Part>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub task_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extensions: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reference_task_ids: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Artifact {
    pub artifact_id: String,
    pub parts: Vec<Part>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extensions: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TaskStatus {
    pub state: TaskState,
    pub timestamp: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<Message>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Task {
    pub id: String,
    pub context_id: String,
    pub status: TaskStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub artifacts: Option<Vec<Artifact>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub history: Option<Vec<Message>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, serde_json::Value>>,
}

// ============================================================================
// AgentCard Metadata
// ============================================================================

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct AgentCardMetadata {
    #[pyo3(get, set)]
    pub promptcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub datacard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub modelcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    #[pyo3(get)]
    pub spec: Option<AgentSpec>,
}

#[pymethods]
impl AgentCardMetadata {
    #[new]
    pub fn new() -> Self {
        Self::default()
    }
}

// ============================================================================
// Main AgentCard
// ============================================================================

#[pyclass]
#[derive(Debug, Serialize, Clone)]
pub struct AgentCard {
    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Vec<String>,

    #[pyo3(get, set)]
    pub metadata: AgentCardMetadata,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub opsml_version: String,
}

#[pymethods]
impl AgentCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (space=None, name=None, version=None, tags=None, spec=None))]
    pub fn new(
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        spec: Option<AgentSpec>,
    ) -> Result<Self, CardError> {
        Self::new_rs(space, name, version, tags, spec)
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    pub fn add_promptcard_uid(&mut self, uid: &str) {
        self.metadata.promptcard_uids.push(uid.to_string());
    }

    pub fn add_datacard_uid(&mut self, uid: &str) {
        self.metadata.datacard_uids.push(uid.to_string());
    }

    pub fn add_modelcard_uid(&mut self, uid: &str) {
        self.metadata.modelcard_uids.push(uid.to_string());
    }

    #[setter]
    pub fn set_experimentcard_uid(&mut self, uid: Option<String>) {
        self.metadata.experimentcard_uid = uid;
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<&str> {
        self.metadata.experimentcard_uid.as_deref()
    }

    #[setter]
    pub fn set_spec(&mut self, spec: AgentSpec) {
        self.metadata.spec = Some(spec);
    }

    #[getter]
    pub fn spec(&self) -> Option<AgentSpec> {
        self.metadata.spec.clone()
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        debug!("Saving AgentCard to path: {:?}", path);

        // Save the main card
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        // If A2A agent card exists, save it separately
        if let Some(a2a_card) = &self.metadata.spec {
            let a2a_save_path = path.join("a2a_agent_card").with_extension(Suffix::Json);
            PyHelperFuncs::save_to_json(&a2a_card, &a2a_save_path)?;
        }

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> Result<AgentCard, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?)
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = AgentCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            experimentcard_uid: self.metadata.experimentcard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            opsml_version: self.opsml_version.clone(),
            promptcard_uids: self.metadata.promptcard_uids.clone(),
            datacard_uids: self.metadata.datacard_uids.clone(),
            modelcard_uids: self.metadata.modelcard_uids.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(CardRecord::Agent(record))
    }

    #[staticmethod]
    pub fn from_path(path: PathBuf) -> Result<Self, CardError> {
        let content = std::fs::read_to_string(&path)?;
        let mut card: AgentCard = serde_json::from_str(&content).inspect_err(|e| {
            error!("Failed to deserialize AgentCard: {e}");
        })?;

        // Try to load A2A agent card if it exists
        let a2a_path = path
            .parent()
            .unwrap()
            .join("a2a_agent_card")
            .with_extension(Suffix::Json);

        if a2a_path.exists() {
            let a2a_content = std::fs::read_to_string(&a2a_path)?;
            let a2a_card: AgentSpec = serde_json::from_str(&a2a_content).inspect_err(|e| {
                error!("Failed to deserialize AgentSpec: {e}");
            })?;
            card.metadata.spec = Some(a2a_card);
        }

        Ok(card)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl AgentCard {
    pub fn new_rs(
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        spec: Option<AgentSpec>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Agent;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)?;
        let tags = tags.unwrap_or_default();

        let mut metadata = AgentCardMetadata::default();
        metadata.spec = spec;

        Ok(Self {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            metadata,
            registry_type,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
        })
    }
}

impl<'de> Deserialize<'de> for AgentCard {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        #[derive(Deserialize)]
        struct AgentCardHelper {
            space: String,
            name: String,
            version: String,
            uid: String,
            tags: Vec<String>,
            metadata: AgentCardMetadata,
            registry_type: RegistryType,
            app_env: String,
            created_at: DateTime<Utc>,
            is_card: bool,
            opsml_version: String,
        }

        let helper = AgentCardHelper::deserialize(deserializer)?;

        Ok(AgentCard {
            space: helper.space,
            name: helper.name,
            version: helper.version,
            uid: helper.uid,
            tags: helper.tags,
            metadata: helper.metadata,
            registry_type: helper.registry_type,
            app_env: helper.app_env,
            created_at: helper.created_at,
            is_card: helper.is_card,
            opsml_version: helper.opsml_version,
        })
    }
}

// ============================================================================
// Python Module Registration Helpers
// ============================================================================
