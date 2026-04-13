use crate::contracts::DeploymentConfig;
use crate::error::AgentConfigError;
use opsml_utils::{PyHelperFuncs, convert_keys_to_snake_case};
use pyo3::{IntoPyObjectExt, prelude::*, types::PyDict};
use pythonize::depythonize;
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use serde_yaml;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
// Validation constants per Agent Skills Spec
const MAX_SKILL_NAME_LENGTH: usize = 64;
const MAX_DESCRIPTION_LENGTH: usize = 1024;
const MAX_COMPATIBILITY_LENGTH: usize = 500;

// Regex patterns for validation
static SKILL_NAME_REGEX: LazyLock<Regex> = LazyLock::new(|| {
    // Matches lowercase alphanumeric and hyphens
    // - Must start and end with alphanumeric
    // - Hyphens only appear between alphanumeric characters (prevents consecutive hyphens)
    Regex::new(r"^[a-z0-9]+(-[a-z0-9]+)*$").unwrap()
});

fn a2a_current_version() -> String {
    "0.3.0".to_string()
}
fn agent_current_version() -> String {
    "0.0.0".to_string()
}

#[pyclass(from_py_object)]
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

// should be all caps (JSONRPC, HTTP+JSON, GRPC) but we'll normalise it in the UI to be more flexible
#[pyclass(eq, eq_int, from_py_object)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "UPPERCASE")]
pub enum ProtocolBinding {
    JsonRpc,
    #[default]
    #[serde(alias = "HTTP+JSON")]
    HttpJson,
    Grpc,
}

impl From<&str> for ProtocolBinding {
    fn from(s: &str) -> Self {
        match s.to_uppercase().replace(&['-', ' ', '+'][..], "_").as_str() {
            "JSONRPC" => ProtocolBinding::JsonRpc,
            "HTTP_JSON" | "HTTP+JSON" => ProtocolBinding::HttpJson,
            "GRPC" => ProtocolBinding::Grpc,
            _ => ProtocolBinding::HttpJson, // default to HTTP+JSON if unrecognized
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentInterface {
    #[pyo3(get, set)]
    pub url: String,

    #[pyo3(get, set)]
    #[serde(alias = "protocol_binding")]
    pub protocol_binding: ProtocolBinding,

    #[pyo3(get, set)]
    #[serde(alias = "protocol_version", default = "a2a_current_version")]
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
        protocol_binding: Bound<'_, PyAny>,
        protocol_version: String,
        tenant: Option<String>,
    ) -> Self {
        // if isinstance of ProtocolBinding, extract the value, otherwise try to convert from string
        let protocol_binding = if protocol_binding.is_instance_of::<ProtocolBinding>() {
            protocol_binding
                .extract::<ProtocolBinding>()
                .unwrap_or_default()
        } else {
            ProtocolBinding::from(
                protocol_binding
                    .extract::<String>()
                    .unwrap_or_default()
                    .as_str(),
            )
        };
        Self {
            url,
            protocol_binding,
            protocol_version,
            tenant: tenant.unwrap_or_default(),
        }
    }
}

impl AgentInterface {
    pub fn new_rs(
        url: String,
        protocol_binding: ProtocolBinding,
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

#[pyclass(from_py_object)]
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
        let depythonized = params.map(|p| depythonize(p).unwrap_or_default());
        Self {
            uri,
            description,
            params: depythonized,
            required,
        }
    }

    #[getter]
    pub fn get_params<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, AgentConfigError> {
        match &self.params {
            Some(params) => Ok(pythonize::pythonize(py, params)?),
            None => Ok(py.None().into_bound_py_any(py)?),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentCapabilities {
    #[pyo3(get, set)]
    pub streaming: bool,

    #[pyo3(get, set)]
    #[serde(alias = "push_notifications")]
    pub push_notifications: bool,

    #[pyo3(get, set)]
    #[serde(alias = "extended_agent_card")]
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

#[pyclass(from_py_object)]
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

/// Claude Agent Skill Standard
/// Implements the Agent Skills specification from https://agentskills.io/specification
#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentSkillStandard {
    #[pyo3(get, set)]
    pub name: String, // lowercase alphanumeric + hyphens only, 1-64 chars

    #[pyo3(get, set)]
    pub description: String, // 1-1024 chars

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub license: Option<String>,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compatibility: Option<String>, // max 500 chars

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, String>>,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "allowed_tools")]
    pub allowed_tools: Option<Vec<String>>,

    // Optional directory path to the skill
    // If None: expected at {parent}/skills/{skill-name}/SKILL.md
    // If Some(path): expected at {path}/SKILL.md, where last directory in path must match skill name
    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "skills_path")]
    pub skills_path: Option<PathBuf>,

    // The actual Markdown body (loaded on demand)
    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<String>,
}

fn split_frontmatter(content: &str) -> Option<(&str, &str)> {
    let content = content.trim_start();
    let rest = content.strip_prefix("---")?;
    let rest = rest
        .strip_prefix('\n')
        .or_else(|| rest.strip_prefix("\r\n"))?;
    let end = rest.find("\n---").or_else(|| rest.find("\r\n---"))?;
    let frontmatter = &rest[..end];
    let after_delim = &rest[end..];
    let body_start = after_delim
        .find('\n')
        .map(|i| {
            let after_nl = &after_delim[i + 1..];
            after_nl
                .find('\n')
                .map(|j| i + 1 + j + 1)
                .unwrap_or(i + 1 + after_nl.len())
        })
        .unwrap_or(after_delim.len());
    Some((frontmatter, &after_delim[body_start..]))
}

impl AgentSkillStandard {
    pub fn to_markdown(&self) -> Result<String, AgentConfigError> {
        let mut skill_for_frontmatter = self.clone();
        skill_for_frontmatter.body = None;
        let mut frontmatter = serde_yaml::to_string(&skill_for_frontmatter)?;
        frontmatter = frontmatter.trim_end().to_string();
        let body = self.body.as_deref().unwrap_or("");
        Ok(format!("---\n{frontmatter}\n---\n{body}"))
    }

    pub fn from_markdown(content: &str) -> Result<Self, AgentConfigError> {
        let (frontmatter, body) = split_frontmatter(content).ok_or_else(|| {
            AgentConfigError::ParseError(
                "Skill markdown is missing YAML frontmatter delimiters (---)".to_string(),
            )
        })?;
        let mut skill: AgentSkillStandard = serde_yaml::from_str(frontmatter)?;
        skill.body = Some(body.to_string());
        Ok(skill)
    }

    /// Validate the name field per Agent Skills specification
    fn validate_name(&self) -> Result<(), AgentConfigError> {
        let name = self.name.trim();

        if name.is_empty() {
            return Err(AgentConfigError::FieldNameEmpty);
        }

        if name.len() > MAX_SKILL_NAME_LENGTH {
            return Err(AgentConfigError::FieldNameTooLong {
                name: name.to_string(),
                length: name.len(),
                max_length: MAX_SKILL_NAME_LENGTH,
            });
        }

        // Check if name is lowercase
        if name != name.to_lowercase() {
            return Err(AgentConfigError::SkillMustBeLowercase {
                name: name.to_string(),
            });
        }

        // Check if name matches the pattern: starts/ends with alphanumeric, no consecutive hyphens
        if !SKILL_NAME_REGEX.is_match(name) {
            let mut error_msg = format!("Skill name '{}' is invalid. ", name);

            if name.starts_with('-') || name.ends_with('-') {
                error_msg.push_str("Name cannot start or end with a hyphen. ");
            }
            if name.contains("--") {
                error_msg.push_str("Name cannot contain consecutive hyphens. ");
            }
            if !name.chars().all(|c| c.is_ascii_alphanumeric() || c == '-') {
                error_msg.push_str("Only lowercase letters, digits, and hyphens are allowed.");
            }

            return Err(AgentConfigError::SkillNameInvalid {
                name: name.to_string(),
                reason: error_msg,
            });
        }

        Ok(())
    }

    /// Validate the description field per Agent Skills specification
    fn validate_description(&self) -> Result<(), AgentConfigError> {
        let description = self.description.trim();

        if description.is_empty() {
            return Err(AgentConfigError::FieldDescriptionEmpty);
        }

        if description.len() > MAX_DESCRIPTION_LENGTH {
            return Err(AgentConfigError::FieldDescriptionTooLong {
                length: description.len(),
                max_length: MAX_DESCRIPTION_LENGTH,
            });
        }

        Ok(())
    }

    /// Validate the compatibility field per Agent Skills specification
    fn validate_compatibility(&self) -> Result<(), AgentConfigError> {
        if let Some(compatibility) = &self.compatibility {
            if compatibility.is_empty() {
                return Err(AgentConfigError::FieldCompatibilityEmpty);
            }

            if compatibility.len() > MAX_COMPATIBILITY_LENGTH {
                return Err(AgentConfigError::FieldCompatibilityTooLong {
                    length: compatibility.len(),
                    max_length: MAX_COMPATIBILITY_LENGTH,
                });
            }
        }

        Ok(())
    }

    /// Validate the skills_path and check if SKILL.md file exists
    /// If parent_dir is provided, it will be used as the base for relative paths. Otherwise, current working directory is used.
    /// It is expected that the last directory in the skills_path matches the skill name, and SKILL.md is located within that directory.
    /// If skills_path is None, it defaults to {parent_dir}/skills/{skill-name}/SKILL.md
    fn validate_skills_path(&self, root_path: &Path) -> Result<(), AgentConfigError> {
        let skill_md_path = match &self.skills_path {
            Some(dir_path) => {
                let resolved_path = if dir_path.is_absolute() {
                    dir_path.clone()
                } else {
                    root_path.join(dir_path)
                };

                if let Some(last_dir) = resolved_path.file_name()
                    && last_dir.to_string_lossy() != self.name
                {
                    return Err(AgentConfigError::LastDirectoryMustMatchSkillName {
                        skills_path: last_dir.to_string_lossy().to_string(),
                        skill_name: self.name.clone(),
                    });
                }

                resolved_path.join("SKILL.md")
            }
            None => root_path.join("skills").join(&self.name).join("SKILL.md"),
        };

        if !skill_md_path.exists() {
            return Err(AgentConfigError::SkillFileNotFound {
                path: skill_md_path.to_string_lossy().to_string(),
            });
        }

        Ok(())
    }

    /// Comprehensive validation of all fields
    pub fn validate(&self, root_path: &Path) -> Result<(), AgentConfigError> {
        self.validate_name()?;

        self.validate_description()?;

        self.validate_compatibility()?;

        self.validate_skills_path(root_path)?;

        Ok(())
    }
}

#[pymethods]

impl AgentSkillStandard {
    #[new]
    #[pyo3(signature = (name, description, license=None, compatibility=None, metadata=None, allowed_tools=None, skills_path=None, body=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        name: String,
        description: String,
        license: Option<String>,
        compatibility: Option<String>,
        metadata: Option<HashMap<String, String>>,
        allowed_tools: Option<Vec<String>>,
        skills_path: Option<PathBuf>,
        body: Option<String>,
    ) -> PyResult<Self> {
        let skill = Self {
            name,
            description,
            license,
            compatibility,
            metadata,
            allowed_tools,
            skills_path,
            body,
        };

        Ok(skill)
    }

    /// Get the expected SKILL.md file path based on skills_path
    /// Returns the full path where SKILL.md should be located
    #[pyo3(name = "get_skill_md_path")]
    pub fn py_get_skill_md_path(&self, parent_dir: Option<String>) -> String {
        let skill_name = self.name.trim();

        let path = match &self.skills_path {
            Some(dir_path) => Path::new(dir_path).join("SKILL.md"),
            None => {
                let base = parent_dir
                    .as_ref()
                    .map(|p| Path::new(p.as_str()))
                    .unwrap_or_else(|| Path::new("."));
                base.join("skills").join(skill_name).join("SKILL.md")
            }
        };

        path.to_string_lossy().to_string()
    }
}

#[pyclass(from_py_object)]
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
    #[serde(alias = "input_modes")]
    pub input_modes: Option<Vec<String>>,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    #[serde(alias = "output_modes")]
    pub output_modes: Option<Vec<String>>,

    #[pyo3(get, set)]
    #[serde(alias = "security_requirements")]
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

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(tag = "format", rename_all = "lowercase")]
pub enum SkillFormat {
    Standard(AgentSkillStandard),
    #[serde(rename = "a2a")]
    A2A(AgentSkill),
}

impl SkillFormat {
    pub fn validate(&self, root_path: &Path) -> Result<(), AgentConfigError> {
        match self {
            SkillFormat::A2A(_skill) => Ok(()),
            SkillFormat::Standard(skill) => skill.validate(root_path),
        }
    }
}

#[pymethods]
impl SkillFormat {
    #[new]
    pub fn new(skill: &Bound<'_, PyAny>) -> Result<Self, AgentConfigError> {
        if skill.is_instance_of::<AgentSkill>() {
            let agent_skill = skill.extract::<AgentSkill>()?;
            Ok(SkillFormat::A2A(agent_skill))
        } else if skill.is_instance_of::<AgentSkillStandard>() {
            let standard_skill = skill.extract::<AgentSkillStandard>()?;
            Ok(SkillFormat::Standard(standard_skill))
        } else {
            Err(AgentConfigError::PyError(format!(
                "Unsupported skill format type: {:?}",
                skill.get_type()
            )))
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ApiKeySecurityScheme {
    #[pyo3(get, set)]
    pub description: Option<String>,
    #[pyo3(get, set)]
    pub location: String,
    #[pyo3(get, set)]
    pub name: String,
}

#[pymethods]
impl ApiKeySecurityScheme {
    #[new]
    #[pyo3(signature = (name, location, description=None))]
    pub fn new(name: String, location: String, description: Option<String>) -> Self {
        Self {
            name,
            location,
            description,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct HttpAuthSecurityScheme {
    #[pyo3(get, set)]
    scheme: String,
    #[pyo3(get, set)]
    #[serde(alias = "bearer_format")]
    bearer_format: String,
    #[pyo3(get, set)]
    description: String,
}

#[pymethods]
impl HttpAuthSecurityScheme {
    #[new]
    #[pyo3(signature = (scheme, bearer_format=None, description=None))]
    pub fn new(scheme: String, bearer_format: Option<String>, description: Option<String>) -> Self {
        Self {
            scheme,
            bearer_format: bearer_format.unwrap_or_default(),
            description: description.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct MtlsSecurityScheme {
    #[pyo3(get, set)]
    description: String,
}

#[pymethods]
impl MtlsSecurityScheme {
    #[new]
    #[pyo3(signature = (description=None))]
    pub fn new(description: Option<String>) -> Self {
        Self {
            description: description.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct Oauth2SecurityScheme {
    #[pyo3(get, set)]
    pub description: Option<String>,
    #[pyo3(get, set)]
    pub flows: OAuthFlows,
    #[pyo3(get, set)]
    #[serde(alias = "oauth2_metadata_url")]
    pub oauth2_metadata_url: Option<String>,
}

#[pymethods]
impl Oauth2SecurityScheme {
    #[new]
    #[pyo3(signature = (flows, description=None, oauth2_metadata_url=None))]
    pub fn new(
        flows: OAuthFlows,
        description: Option<String>,
        oauth2_metadata_url: Option<String>,
    ) -> Self {
        Self {
            flows,
            description,
            oauth2_metadata_url,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OpenIdConnectSecurityScheme {
    #[pyo3(get, set)]
    pub description: Option<String>,
    #[pyo3(get, set)]
    #[serde(alias = "openIdConnectUrl")]
    pub open_id_connect_url: Option<String>,
}

#[pymethods]
impl OpenIdConnectSecurityScheme {
    #[new]
    #[pyo3(signature = (open_id_connect_url=None, description=None))]
    pub fn new(open_id_connect_url: Option<String>, description: Option<String>) -> Self {
        Self {
            open_id_connect_url,
            description,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged, rename_all = "camelCase")]
#[allow(clippy::large_enum_variant)]
pub enum SecurityScheme {
    ApiKeySecurityScheme(ApiKeySecurityScheme),
    HttpAuthSecurityScheme(HttpAuthSecurityScheme),
    MtlsSecurityScheme(MtlsSecurityScheme),
    Oauth2SecurityScheme(Oauth2SecurityScheme),
    OpenIdConnectSecurityScheme(OpenIdConnectSecurityScheme),
}

#[pymethods]
impl SecurityScheme {
    #[new]
    pub fn new(scheme: &Bound<'_, PyAny>) -> Result<Self, AgentConfigError> {
        if scheme.is_instance_of::<ApiKeySecurityScheme>() {
            let api_key_scheme = scheme.extract::<ApiKeySecurityScheme>()?;
            Ok(SecurityScheme::ApiKeySecurityScheme(api_key_scheme))
        } else if scheme.is_instance_of::<HttpAuthSecurityScheme>() {
            let http_auth_scheme = scheme.extract::<HttpAuthSecurityScheme>()?;
            Ok(SecurityScheme::HttpAuthSecurityScheme(http_auth_scheme))
        } else if scheme.is_instance_of::<MtlsSecurityScheme>() {
            let mtls_scheme = scheme.extract::<MtlsSecurityScheme>()?;
            Ok(SecurityScheme::MtlsSecurityScheme(mtls_scheme))
        } else if scheme.is_instance_of::<Oauth2SecurityScheme>() {
            let oauth2_scheme = scheme.extract::<Oauth2SecurityScheme>()?;
            Ok(SecurityScheme::Oauth2SecurityScheme(oauth2_scheme))
        } else if scheme.is_instance_of::<OpenIdConnectSecurityScheme>() {
            let openid_scheme = scheme.extract::<OpenIdConnectSecurityScheme>()?;
            Ok(SecurityScheme::OpenIdConnectSecurityScheme(openid_scheme))
        } else {
            Err(AgentConfigError::PyError(format!(
                "Unsupported security scheme type: {:?}",
                scheme.get_type()
            )))
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OAuthFlows {
    #[pyo3(get, set)]
    #[serde(alias = "authorization_code")]
    pub authorization_code: Option<AuthorizationCodeFlow>,
    #[pyo3(get, set)]
    #[serde(alias = "client_credentials")]
    pub client_credentials: Option<ClientCredentialsFlow>,
    #[pyo3(get, set)]
    #[serde(alias = "device_code")]
    pub device_code: Option<DeviceCodeFlow>,
    #[pyo3(get, set)]
    pub implicit: Option<ImplicitAuthFlow>,
    #[pyo3(get, set)]
    pub password: Option<PassWordAuthFlow>,
}

#[pymethods]
impl OAuthFlows {
    #[new]
    #[pyo3(signature = (authorization_code=None, client_credentials=None, device_code=None, implicit=None, password=None))]
    pub fn new(
        authorization_code: Option<AuthorizationCodeFlow>,
        client_credentials: Option<ClientCredentialsFlow>,
        device_code: Option<DeviceCodeFlow>,
        implicit: Option<ImplicitAuthFlow>,
        password: Option<PassWordAuthFlow>,
    ) -> Self {
        Self {
            authorization_code,
            client_credentials,
            device_code,
            implicit,
            password,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AuthorizationCodeFlow {
    #[pyo3(get, set)]
    #[serde(alias = "authorization_url")]
    pub authorization_url: String,
    #[pyo3(get, set)]
    #[serde(alias = "pkce_required")]
    pub pkce_required: bool,
    #[pyo3(get, set)]
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
    #[serde(alias = "token_url")]
    pub token_url: String,
}

#[pymethods]
impl AuthorizationCodeFlow {
    #[new]
    #[pyo3(signature = (authorization_url, token_url, refresh_url=None, scopes=None, pkce_required=false))]
    pub fn new(
        authorization_url: String,
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
        pkce_required: bool,
    ) -> Self {
        Self {
            authorization_url,
            token_url,
            refresh_url: refresh_url.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
            pkce_required,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ClientCredentialsFlow {
    #[pyo3(get, set)]
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
    #[serde(alias = "token_url")]
    pub token_url: String,
}

#[pymethods]
impl ClientCredentialsFlow {
    #[new]
    #[pyo3(signature = (token_url, refresh_url=None, scopes=None))]
    pub fn new(
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            token_url,
            refresh_url: refresh_url.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct DeviceCodeFlow {
    #[pyo3(get, set)]
    #[serde(alias = "device_authorization_url")]
    pub device_authorization_url: String,
    #[pyo3(get, set)]
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
    #[serde(alias = "token_url")]
    pub token_url: String,
}

#[pymethods]
impl DeviceCodeFlow {
    #[new]
    #[pyo3(signature = (device_authorization_url, token_url, refresh_url=None, scopes=None))]
    pub fn new(
        device_authorization_url: String,
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            device_authorization_url,
            token_url,
            refresh_url: refresh_url.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ImplicitAuthFlow {
    #[pyo3(get, set)]
    #[serde(alias = "authorization_url")]
    pub authorization_url: String,
    #[pyo3(get, set)]
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
}

#[pymethods]
impl ImplicitAuthFlow {
    #[new]
    #[pyo3(signature = (authorization_url, refresh_url=None, scopes=None))]
    pub fn new(
        authorization_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            authorization_url,
            refresh_url: refresh_url.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PassWordAuthFlow {
    #[pyo3(get, set)]
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
    #[serde(alias = "token_url")]
    pub token_url: String,
}

#[pymethods]
impl PassWordAuthFlow {
    #[new]
    #[pyo3(signature = (token_url, refresh_url=None, scopes=None))]
    pub fn new(
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            token_url,
            refresh_url: refresh_url.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentCardSignature {
    #[pyo3(get, set)]
    pub header: Option<HashMap<String, String>>,
    #[pyo3(get, set)]
    pub protected: String,
    #[pyo3(get, set)]
    pub signature: String,
}

#[pymethods]
impl AgentCardSignature {
    #[new]
    #[pyo3(signature = (protected, signature, header=None))]
    pub fn new(
        protected: String,
        signature: String,
        header: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            protected,
            signature,
            header,
        }
    }
}

#[pyclass(from_py_object)]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentSpec {
    #[pyo3(get, set)]
    pub capabilities: AgentCapabilities, // required

    #[pyo3(get, set)]
    #[serde(alias = "default_output_modes")]
    pub default_output_modes: Vec<String>, // required, can be empty

    #[pyo3(get, set)]
    #[serde(alias = "default_input_modes")]
    pub default_input_modes: Vec<String>, // required, can be empty

    #[pyo3(get, set)]
    pub description: String, // required, non-empty

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "documentation_url")]
    pub documentation_url: Option<String>, // not required

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "icon_url")]
    pub icon_url: Option<String>, // not required

    #[pyo3(get, set)]
    pub name: String, // required, non-empty

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<AgentProvider>, // not required

    #[pyo3(get, set)]
    #[serde(
        skip_serializing_if = "Option::is_none",
        alias = "security_requirements"
    )]
    pub security_requirements: Option<Vec<SecurityRequirement>>, // not required

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "security_schemes")]
    pub security_schemes: Option<HashMap<String, SecurityScheme>>, // not required

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signatures: Option<Vec<AgentCardSignature>>, // not required

    #[pyo3(set)]
    pub skills: Vec<SkillFormat>, // required

    #[pyo3(get, set)]
    #[serde(alias = "supported_interfaces")]
    pub supported_interfaces: Vec<AgentInterface>, // required, non-empty

    #[pyo3(get, set)]
    #[serde(default = "agent_current_version")] // required
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
        skills: Vec<Bound<'_, PyAny>>,
        provider: Option<AgentProvider>,
        documentation_url: Option<String>,
        icon_url: Option<String>,
        security_schemes: Option<HashMap<String, SecurityScheme>>,
        security_requirements: Option<Vec<SecurityRequirement>>,
        signatures: Option<Vec<AgentCardSignature>>,
    ) -> Result<Self, AgentConfigError> {
        let mut parsed_skills = Vec::new();
        for skill in skills {
            // check is_instance for AgentSkillStandard and AgentSkill, and parse accordingly
            if skill.is_instance_of::<AgentSkillStandard>() {
                let standard_skill = skill.extract::<AgentSkillStandard>()?;
                parsed_skills.push(SkillFormat::Standard(standard_skill));
            } else if skill.is_instance_of::<AgentSkill>() {
                let a2a_skill = skill.extract::<AgentSkill>()?;
                parsed_skills.push(SkillFormat::A2A(a2a_skill));
            } else {
                // If skill is not a recognized type, skip or handle as needed (here we skip)
                return Err(AgentConfigError::InvalidSkillFormat);
            }
        }

        Ok(Self {
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
            skills: parsed_skills,
            security_schemes,
            security_requirements,
            signatures,
        })
    }

    /// pydantic-style method needed to dump agent spec to Dictionary as part of a2a deployment
    #[pyo3(signature = (**kwargs))]
    #[allow(unused_variables)]
    pub fn model_dump<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Bound<'py, PyAny>, AgentConfigError> {
        let cloned_config = self.clone();
        let camel_case_json = serde_json::to_value(cloned_config)?;
        let snake_case_json = convert_keys_to_snake_case(camel_case_json);
        let pythonized_spec = pythonize::pythonize(py, &snake_case_json)?;
        Ok(pythonized_spec)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn supports_authenticated_extended_card(&self) {}

    #[getter]
    pub fn get_skills<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Vec<Bound<'py, PyAny>>, AgentConfigError> {
        self.skills
            .iter()
            .map(|skill| match skill {
                SkillFormat::Standard(s) => s
                    .clone()
                    .into_bound_py_any(py)
                    .map_err(|e| AgentConfigError::PyError(e.to_string())),
                SkillFormat::A2A(s) => s
                    .clone()
                    .into_bound_py_any(py)
                    .map_err(|e| AgentConfigError::PyError(e.to_string())),
            })
            .collect()
    }
}

impl AgentSpec {
    #[allow(clippy::too_many_arguments)]
    pub fn new_rs(
        name: String,
        description: String,
        version: String,
        supported_interfaces: Vec<AgentInterface>,
        capabilities: AgentCapabilities,
        default_input_modes: Vec<String>,
        default_output_modes: Vec<String>,
        skills: Vec<SkillFormat>,
        provider: Option<AgentProvider>,
        documentation_url: Option<String>,
        icon_url: Option<String>,
        security_schemes: Option<HashMap<String, SecurityScheme>>,
        security_requirements: Option<Vec<SecurityRequirement>>,
        signatures: Option<Vec<AgentCardSignature>>,
    ) -> Result<Self, AgentConfigError> {
        Ok(Self {
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
        })
    }

    /// Validate all skills in the agent spec
    /// For skills in Standard format, also validate their fields and check for SKILL.md file existence
    /// If supported_interfaces is empty, attempt to populate it from deploy_config URLs. If deploy_config is None or contains no URLs, return an error since supported_interfaces cannot be empty.
    pub(crate) fn validate(
        &mut self,
        root_path: &Path,
        deploy_config: &Option<Vec<DeploymentConfig>>,
    ) -> Result<(), AgentConfigError> {
        for skill in &self.skills {
            skill.validate(root_path)?;
        }

        if self.supported_interfaces.is_empty() {
            let Some(deploy_configs) = deploy_config else {
                return Err(AgentConfigError::InterfaceUrlMissing);
            };

            let all_urls: Vec<String> = deploy_configs
                .iter()
                .flat_map(|config| config.urls.iter().cloned())
                .collect();

            if all_urls.is_empty() {
                return Err(AgentConfigError::InterfaceUrlMissing);
            }

            self.supported_interfaces = all_urls
                .into_iter()
                .map(|url| AgentInterface {
                    url,
                    protocol_binding: ProtocolBinding::HttpJson,
                    protocol_version: a2a_current_version(),
                    tenant: String::new(),
                })
                .collect();
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_split_frontmatter_edge_cases() {
        assert!(AgentSkillStandard::from_markdown("no delimiters here").is_err());
        assert!(AgentSkillStandard::from_markdown("---\nkey: value\n").is_err());

        let crlf = "---\r\nname: crlf-skill\r\ndescription: test\r\n---\r\nbody text\r\n";
        let skill = AgentSkillStandard::from_markdown(crlf).unwrap();
        assert_eq!(skill.name, "crlf-skill");
        let body = skill.body.as_deref().unwrap_or("");
        assert!(!body.starts_with("---"));
        assert!(body.contains("body text"));

        let empty_body = "---\nname: empty-body-skill\ndescription: test\n---\n";
        let skill = AgentSkillStandard::from_markdown(empty_body).unwrap();
        assert_eq!(skill.body.as_deref().unwrap_or("non-empty"), "");
    }

    #[test]
    fn test_to_markdown_body_not_in_frontmatter() {
        let skill = AgentSkillStandard {
            name: "fm-test".to_string(),
            description: "test".to_string(),
            license: None,
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: None,
            body: Some("# Steps\n\nDo the thing.\n".to_string()),
        };
        let md = skill.to_markdown().unwrap();
        let close = md.find("\n---\n").unwrap();
        let frontmatter_section = &md[..close];
        assert!(!frontmatter_section.contains("body:"));
        let restored = AgentSkillStandard::from_markdown(&md).unwrap();
        assert!(
            restored
                .body
                .as_deref()
                .unwrap_or("")
                .contains("Do the thing.")
        );
    }

    #[test]
    fn test_to_markdown_roundtrip() {
        let skill = AgentSkillStandard {
            name: "roundtrip".to_string(),
            description: "Roundtrip test".to_string(),
            license: Some("MIT".to_string()),
            compatibility: None,
            metadata: None,
            allowed_tools: Some(vec!["Bash".to_string()]),
            skills_path: None,
            body: Some("# Instructions\n\nDo the thing.\n".to_string()),
        };
        let md = skill.to_markdown().unwrap();
        let restored = AgentSkillStandard::from_markdown(&md).unwrap();
        assert_eq!(restored.name, skill.name);
        assert_eq!(restored.description, skill.description);
        assert_eq!(restored.license, skill.license);
        assert_eq!(restored.allowed_tools, skill.allowed_tools);
        assert_eq!(restored.body, skill.body);
    }
}
