use crate::contracts::DeploymentConfig;
use crate::error::AgentConfigError;
#[cfg(feature = "python")]
use opsml_utils::PyHelperFuncs;
#[cfg(feature = "python")]
use opsml_utils::convert_keys_to_snake_case;
#[cfg(feature = "python")]
use pyo3::{IntoPyObjectExt, prelude::*, types::PyDict};
#[cfg(feature = "python")]
use pythonize::depythonize;
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use serde_yaml;
use std::collections::HashMap;
#[cfg(feature = "python")]
use std::net::IpAddr;
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

#[cfg(feature = "python")]
fn validate_agent_url(url: &str) -> Result<(), AgentConfigError> {
    if url.is_empty() {
        return Err(AgentConfigError::InvalidAgentUrl(
            "URL cannot be empty".to_string(),
        ));
    }

    let lower = url.to_lowercase();

    if lower.starts_with("file://") || lower.starts_with("ftp://") {
        return Err(AgentConfigError::InvalidAgentUrl(format!(
            "URL scheme not permitted: {url}"
        )));
    }

    if lower.starts_with("http://") {
        let host = lower
            .strip_prefix("http://")
            .unwrap_or("")
            .split('/')
            .next()
            .unwrap_or("")
            .split(':')
            .next()
            .unwrap_or("");
        if host != "localhost" && host != "127.0.0.1" {
            return Err(AgentConfigError::InvalidAgentUrl(format!(
                "Only https:// is permitted outside localhost: {url}"
            )));
        }
        return Ok(());
    }

    if !lower.starts_with("https://") {
        return Err(AgentConfigError::InvalidAgentUrl(format!(
            "URL must use https:// scheme: {url}"
        )));
    }

    let host = url[8..]
        .split('/')
        .next()
        .unwrap_or("")
        .split(':')
        .next()
        .unwrap_or("");

    if let Ok(IpAddr::V4(ip)) = host.parse::<IpAddr>() {
        let [a, b, ..] = ip.octets();
        if a == 10
            || (a == 172 && (16..=31).contains(&b))
            || (a == 192 && b == 168)
            || (a == 169 && b == 254)
        {
            return Err(AgentConfigError::InvalidAgentUrl(format!(
                "Private/IMDS IP address not permitted: {url}"
            )));
        }
    }

    Ok(())
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentProvider {
    pub organization: String,
    pub url: String,
}

impl AgentProvider {
    pub fn new(organization: Option<String>, url: Option<String>) -> Self {
        Self {
            organization: organization.unwrap_or_default(),
            url: url.unwrap_or_default(),
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl AgentProvider {
    #[new]
    pub fn py_new(organization: Option<String>, url: Option<String>) -> PyResult<Self> {
        if let Some(ref u) = url {
            validate_agent_url(u).map_err(PyErr::from)?;
        }
        Ok(Self::new(organization, url))
    }

    #[getter]
    pub fn organization(&self) -> String {
        self.organization.clone()
    }

    #[setter]
    pub fn set_organization(&mut self, val: String) {
        self.organization = val;
    }

    #[getter]
    pub fn url(&self) -> String {
        self.url.clone()
    }

    #[setter]
    pub fn set_url(&mut self, val: String) {
        self.url = val;
    }
}

// should be all caps (JSONRPC, HTTP+JSON, GRPC) but we'll normalise it in the UI to be more flexible
#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "UPPERCASE")]
pub enum ProtocolBinding {
    JsonRpc,
    #[default]
    #[serde(rename = "HTTP+JSON", alias = "HTTPJSON")]
    HttpJson,
    Grpc,
}

impl From<&str> for ProtocolBinding {
    fn from(s: &str) -> Self {
        match s.to_uppercase().replace(&['-', ' ', '+'][..], "_").as_str() {
            "JSONRPC" => ProtocolBinding::JsonRpc,
            "HTTP_JSON" => ProtocolBinding::HttpJson,
            "GRPC" => ProtocolBinding::Grpc,
            _ => ProtocolBinding::HttpJson, // default to HTTP+JSON if unrecognized
        }
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentInterface {
    pub url: String,

    #[serde(alias = "protocol_binding")]
    pub protocol_binding: ProtocolBinding,

    #[serde(alias = "protocol_version", default = "a2a_current_version")]
    pub protocol_version: String,

    pub tenant: String,
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

#[cfg(feature = "python")]
#[pymethods]
impl AgentInterface {
    #[new]
    #[pyo3(signature = (url, protocol_binding, protocol_version, tenant=None))]
    pub fn new(
        url: String,
        protocol_binding: Bound<'_, PyAny>,
        protocol_version: String,
        tenant: Option<String>,
    ) -> PyResult<Self> {
        validate_agent_url(&url).map_err(PyErr::from)?;
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
        Ok(Self {
            url,
            protocol_binding,
            protocol_version,
            tenant: tenant.unwrap_or_default(),
        })
    }

    #[getter]
    pub fn url(&self) -> String {
        self.url.clone()
    }

    #[setter]
    pub fn set_url(&mut self, val: String) {
        self.url = val;
    }

    #[getter]
    pub fn protocol_binding(&self) -> ProtocolBinding {
        self.protocol_binding.clone()
    }

    #[setter]
    pub fn set_protocol_binding(&mut self, val: ProtocolBinding) {
        self.protocol_binding = val;
    }

    #[getter]
    pub fn protocol_version(&self) -> String {
        self.protocol_version.clone()
    }

    #[setter]
    pub fn set_protocol_version(&mut self, val: String) {
        self.protocol_version = val;
    }

    #[getter]
    pub fn tenant(&self) -> String {
        self.tenant.clone()
    }

    #[setter]
    pub fn set_tenant(&mut self, val: String) {
        self.tenant = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentExtension {
    pub description: Option<String>,
    pub params: Option<Value>,
    pub required: bool,
    pub uri: String,
}

impl AgentExtension {
    pub fn new_rs(
        uri: String,
        description: Option<String>,
        params: Option<Value>,
        required: bool,
    ) -> Self {
        Self {
            uri,
            description,
            params,
            required,
        }
    }
}

#[cfg(feature = "python")]
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
    pub fn description(&self) -> Option<String> {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: Option<String>) {
        self.description = val;
    }

    #[getter]
    pub fn get_params<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, AgentConfigError> {
        match &self.params {
            Some(params) => Ok(pythonize::pythonize(py, params)?),
            None => Ok(py.None().into_bound_py_any(py)?),
        }
    }

    #[setter]
    pub fn set_params(&mut self, val: Option<&Bound<'_, PyAny>>) {
        self.params = val.map(|p| depythonize(p).unwrap_or_default());
    }

    #[getter]
    pub fn required(&self) -> bool {
        self.required
    }

    #[setter]
    pub fn set_required(&mut self, val: bool) {
        self.required = val;
    }

    #[getter]
    pub fn uri(&self) -> String {
        self.uri.clone()
    }

    #[setter]
    pub fn set_uri(&mut self, val: String) {
        self.uri = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentCapabilities {
    pub streaming: bool,

    #[serde(alias = "push_notifications")]
    pub push_notifications: bool,

    #[serde(alias = "extended_agent_card")]
    pub extended_agent_card: bool,

    pub extensions: Vec<AgentExtension>,
}

impl AgentCapabilities {
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

#[cfg(feature = "python")]
#[pymethods]
impl AgentCapabilities {
    #[new]
    #[pyo3(signature = (streaming=false, push_notifications=false, extended_agent_card=false, extensions=None))]
    pub fn py_new(
        streaming: bool,
        push_notifications: bool,
        extended_agent_card: bool,
        extensions: Option<Vec<AgentExtension>>,
    ) -> Self {
        Self::new(
            streaming,
            push_notifications,
            extended_agent_card,
            extensions,
        )
    }

    #[getter]
    pub fn streaming(&self) -> bool {
        self.streaming
    }

    #[setter]
    pub fn set_streaming(&mut self, val: bool) {
        self.streaming = val;
    }

    #[getter]
    pub fn push_notifications(&self) -> bool {
        self.push_notifications
    }

    #[setter]
    pub fn set_push_notifications(&mut self, val: bool) {
        self.push_notifications = val;
    }

    #[getter]
    pub fn extended_agent_card(&self) -> bool {
        self.extended_agent_card
    }

    #[setter]
    pub fn set_extended_agent_card(&mut self, val: bool) {
        self.extended_agent_card = val;
    }

    #[getter]
    pub fn extensions(&self) -> Vec<AgentExtension> {
        self.extensions.clone()
    }

    #[setter]
    pub fn set_extensions(&mut self, val: Vec<AgentExtension>) {
        self.extensions = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct SecurityRequirement {
    pub schemes: Vec<String>,
}

impl SecurityRequirement {
    pub fn new(schemes: Vec<String>) -> Self {
        Self { schemes }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl SecurityRequirement {
    #[new]
    pub fn py_new(schemes: Vec<String>) -> Self {
        Self::new(schemes)
    }

    #[getter]
    pub fn schemes(&self) -> Vec<String> {
        self.schemes.clone()
    }

    #[setter]
    pub fn set_schemes(&mut self, val: Vec<String>) {
        self.schemes = val;
    }
}

/// Claude Agent Skill Standard
/// Implements the Agent Skills specification from https://agentskills.io/specification
#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentSkillStandard {
    pub name: String, // lowercase alphanumeric + hyphens only, 1-64 chars

    pub description: String, // 1-1024 chars

    #[serde(skip_serializing_if = "Option::is_none")]
    pub license: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub compatibility: Option<String>, // max 500 chars

    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, String>>,

    #[serde(skip_serializing_if = "Option::is_none", alias = "allowed_tools")]
    pub allowed_tools: Option<Vec<String>>,

    // Optional directory path to the skill
    // If None: expected at {parent}/skills/{skill-name}/SKILL.md
    // If Some(path): expected at {path}/SKILL.md, where last directory in path must match skill name
    #[serde(skip_serializing_if = "Option::is_none", alias = "skills_path")]
    pub skills_path: Option<PathBuf>,

    // The actual Markdown body (loaded on demand)
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

    /// Get the expected SKILL.md file path based on skills_path
    /// Returns the full path where SKILL.md should be located
    pub fn get_skill_md_path(&self, parent_dir: Option<String>) -> String {
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

#[cfg(feature = "python")]
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
        self.get_skill_md_path(parent_dir)
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: String) {
        self.description = val;
    }

    #[getter]
    pub fn license(&self) -> Option<String> {
        self.license.clone()
    }

    #[setter]
    pub fn set_license(&mut self, val: Option<String>) {
        self.license = val;
    }

    #[getter]
    pub fn compatibility(&self) -> Option<String> {
        self.compatibility.clone()
    }

    #[setter]
    pub fn set_compatibility(&mut self, val: Option<String>) {
        self.compatibility = val;
    }

    #[getter]
    pub fn metadata(&self) -> Option<HashMap<String, String>> {
        self.metadata.clone()
    }

    #[setter]
    pub fn set_metadata(&mut self, val: Option<HashMap<String, String>>) {
        self.metadata = val;
    }

    #[getter]
    pub fn allowed_tools(&self) -> Option<Vec<String>> {
        self.allowed_tools.clone()
    }

    #[setter]
    pub fn set_allowed_tools(&mut self, val: Option<Vec<String>>) {
        self.allowed_tools = val;
    }

    #[getter]
    pub fn skills_path(&self) -> Option<PathBuf> {
        self.skills_path.clone()
    }

    #[setter]
    pub fn set_skills_path(&mut self, val: Option<PathBuf>) {
        self.skills_path = val;
    }

    #[getter]
    pub fn body(&self) -> Option<String> {
        self.body.clone()
    }

    #[setter]
    pub fn set_body(&mut self, val: Option<String>) {
        self.body = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(rename_all = "camelCase", default)]
pub struct AgentSkill {
    pub description: String,

    pub examples: Vec<String>,

    pub id: String,

    #[serde(alias = "input_modes")]
    pub input_modes: Option<Vec<String>>,

    pub name: String,

    #[serde(alias = "output_modes")]
    pub output_modes: Option<Vec<String>>,

    #[serde(alias = "security_requirements")]
    pub security_requirements: Option<Vec<SecurityRequirement>>,

    pub tags: Vec<String>,
}

impl AgentSkill {
    #[allow(clippy::too_many_arguments)]
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

#[cfg(feature = "python")]
#[pymethods]
impl AgentSkill {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (id, name, description, tags=None, examples=None, input_modes=None, output_modes=None, security_requirements=None))]
    pub fn py_new(
        id: String,
        name: String,
        description: String,
        tags: Option<Vec<String>>,
        examples: Option<Vec<String>>,
        input_modes: Option<Vec<String>>,
        output_modes: Option<Vec<String>>,
        security_requirements: Option<Vec<SecurityRequirement>>,
    ) -> Self {
        Self::new(
            id,
            name,
            description,
            tags,
            examples,
            input_modes,
            output_modes,
            security_requirements,
        )
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: String) {
        self.description = val;
    }

    #[getter]
    pub fn examples(&self) -> Vec<String> {
        self.examples.clone()
    }

    #[setter]
    pub fn set_examples(&mut self, val: Vec<String>) {
        self.examples = val;
    }

    #[getter]
    pub fn id(&self) -> String {
        self.id.clone()
    }

    #[setter]
    pub fn set_id(&mut self, val: String) {
        self.id = val;
    }

    #[getter]
    pub fn input_modes(&self) -> Option<Vec<String>> {
        self.input_modes.clone()
    }

    #[setter]
    pub fn set_input_modes(&mut self, val: Option<Vec<String>>) {
        self.input_modes = val;
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn output_modes(&self) -> Option<Vec<String>> {
        self.output_modes.clone()
    }

    #[setter]
    pub fn set_output_modes(&mut self, val: Option<Vec<String>>) {
        self.output_modes = val;
    }

    #[getter]
    pub fn security_requirements(&self) -> Option<Vec<SecurityRequirement>> {
        self.security_requirements.clone()
    }

    #[setter]
    pub fn set_security_requirements(&mut self, val: Option<Vec<SecurityRequirement>>) {
        self.security_requirements = val;
    }

    #[getter]
    pub fn tags(&self) -> Vec<String> {
        self.tags.clone()
    }

    #[setter]
    pub fn set_tags(&mut self, val: Vec<String>) {
        self.tags = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
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

#[cfg(feature = "python")]
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

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ApiKeySecurityScheme {
    pub description: Option<String>,
    pub location: String,
    pub name: String,
}

impl ApiKeySecurityScheme {
    pub fn new(name: String, location: String, description: Option<String>) -> Self {
        Self {
            name,
            location,
            description,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl ApiKeySecurityScheme {
    #[new]
    #[pyo3(signature = (name, location, description=None))]
    pub fn py_new(name: String, location: String, description: Option<String>) -> Self {
        Self::new(name, location, description)
    }

    #[getter]
    pub fn description(&self) -> Option<String> {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: Option<String>) {
        self.description = val;
    }

    #[getter]
    pub fn location(&self) -> String {
        self.location.clone()
    }

    #[setter]
    pub fn set_location(&mut self, val: String) {
        self.location = val;
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct HttpAuthSecurityScheme {
    pub scheme: String,
    #[serde(alias = "bearer_format")]
    pub bearer_format: String,
    pub description: String,
}

impl HttpAuthSecurityScheme {
    pub fn new(scheme: String, bearer_format: Option<String>, description: Option<String>) -> Self {
        Self {
            scheme,
            bearer_format: bearer_format.unwrap_or_default(),
            description: description.unwrap_or_default(),
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl HttpAuthSecurityScheme {
    #[new]
    #[pyo3(signature = (scheme, bearer_format=None, description=None))]
    pub fn py_new(
        scheme: String,
        bearer_format: Option<String>,
        description: Option<String>,
    ) -> Self {
        Self::new(scheme, bearer_format, description)
    }

    #[getter]
    pub fn scheme(&self) -> String {
        self.scheme.clone()
    }

    #[setter]
    pub fn set_scheme(&mut self, val: String) {
        self.scheme = val;
    }

    #[getter]
    pub fn bearer_format(&self) -> String {
        self.bearer_format.clone()
    }

    #[setter]
    pub fn set_bearer_format(&mut self, val: String) {
        self.bearer_format = val;
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: String) {
        self.description = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct MtlsSecurityScheme {
    pub description: String,
}

impl MtlsSecurityScheme {
    pub fn new(description: Option<String>) -> Self {
        Self {
            description: description.unwrap_or_default(),
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl MtlsSecurityScheme {
    #[new]
    #[pyo3(signature = (description=None))]
    pub fn py_new(description: Option<String>) -> Self {
        Self::new(description)
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: String) {
        self.description = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct Oauth2SecurityScheme {
    pub description: Option<String>,
    pub flows: OAuthFlows,
    #[serde(alias = "oauth2_metadata_url")]
    pub oauth2_metadata_url: Option<String>,
}

impl Oauth2SecurityScheme {
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

#[cfg(feature = "python")]
#[pymethods]
impl Oauth2SecurityScheme {
    #[new]
    #[pyo3(signature = (flows, description=None, oauth2_metadata_url=None))]
    pub fn py_new(
        flows: OAuthFlows,
        description: Option<String>,
        oauth2_metadata_url: Option<String>,
    ) -> Self {
        Self::new(flows, description, oauth2_metadata_url)
    }

    #[getter]
    pub fn description(&self) -> Option<String> {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: Option<String>) {
        self.description = val;
    }

    #[getter]
    pub fn flows(&self) -> OAuthFlows {
        self.flows.clone()
    }

    #[setter]
    pub fn set_flows(&mut self, val: OAuthFlows) {
        self.flows = val;
    }

    #[getter]
    pub fn oauth2_metadata_url(&self) -> Option<String> {
        self.oauth2_metadata_url.clone()
    }

    #[setter]
    pub fn set_oauth2_metadata_url(&mut self, val: Option<String>) {
        self.oauth2_metadata_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OpenIdConnectSecurityScheme {
    pub description: Option<String>,
    #[serde(alias = "openIdConnectUrl")]
    pub open_id_connect_url: Option<String>,
}

impl OpenIdConnectSecurityScheme {
    pub fn new(open_id_connect_url: Option<String>, description: Option<String>) -> Self {
        Self {
            open_id_connect_url,
            description,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl OpenIdConnectSecurityScheme {
    #[new]
    #[pyo3(signature = (open_id_connect_url=None, description=None))]
    pub fn py_new(open_id_connect_url: Option<String>, description: Option<String>) -> Self {
        Self::new(open_id_connect_url, description)
    }

    #[getter]
    pub fn description(&self) -> Option<String> {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: Option<String>) {
        self.description = val;
    }

    #[getter]
    pub fn open_id_connect_url(&self) -> Option<String> {
        self.open_id_connect_url.clone()
    }

    #[setter]
    pub fn set_open_id_connect_url(&mut self, val: Option<String>) {
        self.open_id_connect_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
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

#[cfg(feature = "python")]
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

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OAuthFlows {
    #[serde(alias = "authorization_code")]
    pub authorization_code: Option<AuthorizationCodeFlow>,
    #[serde(alias = "client_credentials")]
    pub client_credentials: Option<ClientCredentialsFlow>,
    #[serde(alias = "device_code")]
    pub device_code: Option<DeviceCodeFlow>,
    pub implicit: Option<ImplicitAuthFlow>,
    pub password: Option<PasswordAuthFlow>,
}

impl OAuthFlows {
    pub fn new(
        authorization_code: Option<AuthorizationCodeFlow>,
        client_credentials: Option<ClientCredentialsFlow>,
        device_code: Option<DeviceCodeFlow>,
        implicit: Option<ImplicitAuthFlow>,
        password: Option<PasswordAuthFlow>,
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

#[cfg(feature = "python")]
#[pymethods]
impl OAuthFlows {
    #[new]
    #[pyo3(signature = (authorization_code=None, client_credentials=None, device_code=None, implicit=None, password=None))]
    pub fn py_new(
        authorization_code: Option<AuthorizationCodeFlow>,
        client_credentials: Option<ClientCredentialsFlow>,
        device_code: Option<DeviceCodeFlow>,
        implicit: Option<ImplicitAuthFlow>,
        password: Option<PasswordAuthFlow>,
    ) -> Self {
        Self::new(
            authorization_code,
            client_credentials,
            device_code,
            implicit,
            password,
        )
    }

    #[getter]
    pub fn authorization_code(&self) -> Option<AuthorizationCodeFlow> {
        self.authorization_code.clone()
    }

    #[setter]
    pub fn set_authorization_code(&mut self, val: Option<AuthorizationCodeFlow>) {
        self.authorization_code = val;
    }

    #[getter]
    pub fn client_credentials(&self) -> Option<ClientCredentialsFlow> {
        self.client_credentials.clone()
    }

    #[setter]
    pub fn set_client_credentials(&mut self, val: Option<ClientCredentialsFlow>) {
        self.client_credentials = val;
    }

    #[getter]
    pub fn device_code(&self) -> Option<DeviceCodeFlow> {
        self.device_code.clone()
    }

    #[setter]
    pub fn set_device_code(&mut self, val: Option<DeviceCodeFlow>) {
        self.device_code = val;
    }

    #[getter]
    pub fn implicit(&self) -> Option<ImplicitAuthFlow> {
        self.implicit.clone()
    }

    #[setter]
    pub fn set_implicit(&mut self, val: Option<ImplicitAuthFlow>) {
        self.implicit = val;
    }

    #[getter]
    pub fn password(&self) -> Option<PasswordAuthFlow> {
        self.password.clone()
    }

    #[setter]
    pub fn set_password(&mut self, val: Option<PasswordAuthFlow>) {
        self.password = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AuthorizationCodeFlow {
    #[serde(alias = "authorization_url")]
    pub authorization_url: String,
    #[serde(alias = "pkce_required")]
    pub pkce_required: bool,
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    #[serde(alias = "token_url")]
    pub token_url: String,
}

impl AuthorizationCodeFlow {
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

#[cfg(feature = "python")]
#[pymethods]
impl AuthorizationCodeFlow {
    #[new]
    #[pyo3(signature = (authorization_url, token_url, refresh_url=None, scopes=None, pkce_required=false))]
    pub fn py_new(
        authorization_url: String,
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
        pkce_required: bool,
    ) -> Self {
        Self::new(
            authorization_url,
            token_url,
            refresh_url,
            scopes,
            pkce_required,
        )
    }

    #[getter]
    pub fn authorization_url(&self) -> String {
        self.authorization_url.clone()
    }

    #[setter]
    pub fn set_authorization_url(&mut self, val: String) {
        self.authorization_url = val;
    }

    #[getter]
    pub fn pkce_required(&self) -> bool {
        self.pkce_required
    }

    #[setter]
    pub fn set_pkce_required(&mut self, val: bool) {
        self.pkce_required = val;
    }

    #[getter]
    pub fn refresh_url(&self) -> String {
        self.refresh_url.clone()
    }

    #[setter]
    pub fn set_refresh_url(&mut self, val: String) {
        self.refresh_url = val;
    }

    #[getter]
    pub fn scopes(&self) -> HashMap<String, String> {
        self.scopes.clone()
    }

    #[setter]
    pub fn set_scopes(&mut self, val: HashMap<String, String>) {
        self.scopes = val;
    }

    #[getter]
    pub fn token_url(&self) -> String {
        self.token_url.clone()
    }

    #[setter]
    pub fn set_token_url(&mut self, val: String) {
        self.token_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ClientCredentialsFlow {
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    #[serde(alias = "token_url")]
    pub token_url: String,
}

impl ClientCredentialsFlow {
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

#[cfg(feature = "python")]
#[pymethods]
impl ClientCredentialsFlow {
    #[new]
    #[pyo3(signature = (token_url, refresh_url=None, scopes=None))]
    pub fn py_new(
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self::new(token_url, refresh_url, scopes)
    }

    #[getter]
    pub fn refresh_url(&self) -> String {
        self.refresh_url.clone()
    }

    #[setter]
    pub fn set_refresh_url(&mut self, val: String) {
        self.refresh_url = val;
    }

    #[getter]
    pub fn scopes(&self) -> HashMap<String, String> {
        self.scopes.clone()
    }

    #[setter]
    pub fn set_scopes(&mut self, val: HashMap<String, String>) {
        self.scopes = val;
    }

    #[getter]
    pub fn token_url(&self) -> String {
        self.token_url.clone()
    }

    #[setter]
    pub fn set_token_url(&mut self, val: String) {
        self.token_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct DeviceCodeFlow {
    #[serde(alias = "device_authorization_url")]
    pub device_authorization_url: String,
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    #[serde(alias = "token_url")]
    pub token_url: String,
}

impl DeviceCodeFlow {
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

#[cfg(feature = "python")]
#[pymethods]
impl DeviceCodeFlow {
    #[new]
    #[pyo3(signature = (device_authorization_url, token_url, refresh_url=None, scopes=None))]
    pub fn py_new(
        device_authorization_url: String,
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self::new(device_authorization_url, token_url, refresh_url, scopes)
    }

    #[getter]
    pub fn device_authorization_url(&self) -> String {
        self.device_authorization_url.clone()
    }

    #[setter]
    pub fn set_device_authorization_url(&mut self, val: String) {
        self.device_authorization_url = val;
    }

    #[getter]
    pub fn refresh_url(&self) -> String {
        self.refresh_url.clone()
    }

    #[setter]
    pub fn set_refresh_url(&mut self, val: String) {
        self.refresh_url = val;
    }

    #[getter]
    pub fn scopes(&self) -> HashMap<String, String> {
        self.scopes.clone()
    }

    #[setter]
    pub fn set_scopes(&mut self, val: HashMap<String, String>) {
        self.scopes = val;
    }

    #[getter]
    pub fn token_url(&self) -> String {
        self.token_url.clone()
    }

    #[setter]
    pub fn set_token_url(&mut self, val: String) {
        self.token_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ImplicitAuthFlow {
    #[serde(alias = "authorization_url")]
    pub authorization_url: String,
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
}

impl ImplicitAuthFlow {
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

#[cfg(feature = "python")]
#[pymethods]
impl ImplicitAuthFlow {
    #[new]
    #[pyo3(signature = (authorization_url, refresh_url=None, scopes=None))]
    pub fn py_new(
        authorization_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self::new(authorization_url, refresh_url, scopes)
    }

    #[getter]
    pub fn authorization_url(&self) -> String {
        self.authorization_url.clone()
    }

    #[setter]
    pub fn set_authorization_url(&mut self, val: String) {
        self.authorization_url = val;
    }

    #[getter]
    pub fn refresh_url(&self) -> String {
        self.refresh_url.clone()
    }

    #[setter]
    pub fn set_refresh_url(&mut self, val: String) {
        self.refresh_url = val;
    }

    #[getter]
    pub fn scopes(&self) -> HashMap<String, String> {
        self.scopes.clone()
    }

    #[setter]
    pub fn set_scopes(&mut self, val: HashMap<String, String>) {
        self.scopes = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object, name = "PassWordAuthFlow"))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PasswordAuthFlow {
    #[serde(alias = "refresh_url")]
    pub refresh_url: String,
    pub scopes: HashMap<String, String>,
    #[serde(alias = "token_url")]
    pub token_url: String,
}

impl PasswordAuthFlow {
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

#[cfg(feature = "python")]
#[pymethods]
impl PasswordAuthFlow {
    #[new]
    #[pyo3(signature = (token_url, refresh_url=None, scopes=None))]
    pub fn py_new(
        token_url: String,
        refresh_url: Option<String>,
        scopes: Option<HashMap<String, String>>,
    ) -> Self {
        Self::new(token_url, refresh_url, scopes)
    }

    #[getter]
    pub fn refresh_url(&self) -> String {
        self.refresh_url.clone()
    }

    #[setter]
    pub fn set_refresh_url(&mut self, val: String) {
        self.refresh_url = val;
    }

    #[getter]
    pub fn scopes(&self) -> HashMap<String, String> {
        self.scopes.clone()
    }

    #[setter]
    pub fn set_scopes(&mut self, val: HashMap<String, String>) {
        self.scopes = val;
    }

    #[getter]
    pub fn token_url(&self) -> String {
        self.token_url.clone()
    }

    #[setter]
    pub fn set_token_url(&mut self, val: String) {
        self.token_url = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentCardSignature {
    pub header: Option<HashMap<String, String>>,
    pub protected: String,
    pub signature: String,
}

impl AgentCardSignature {
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

#[cfg(feature = "python")]
#[pymethods]
impl AgentCardSignature {
    #[new]
    #[pyo3(signature = (protected, signature, header=None))]
    pub fn py_new(
        protected: String,
        signature: String,
        header: Option<HashMap<String, String>>,
    ) -> Self {
        Self::new(protected, signature, header)
    }

    #[getter]
    pub fn header(&self) -> Option<HashMap<String, String>> {
        self.header.clone()
    }

    #[setter]
    pub fn set_header(&mut self, val: Option<HashMap<String, String>>) {
        self.header = val;
    }

    #[getter]
    pub fn protected(&self) -> String {
        self.protected.clone()
    }

    #[setter]
    pub fn set_protected(&mut self, val: String) {
        self.protected = val;
    }

    #[getter]
    pub fn signature(&self) -> String {
        self.signature.clone()
    }

    #[setter]
    pub fn set_signature(&mut self, val: String) {
        self.signature = val;
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentSpec {
    pub capabilities: AgentCapabilities, // required

    #[serde(alias = "default_output_modes")]
    pub default_output_modes: Vec<String>, // required, can be empty

    #[serde(alias = "default_input_modes")]
    pub default_input_modes: Vec<String>, // required, can be empty

    pub description: String, // required, non-empty

    #[serde(skip_serializing_if = "Option::is_none", alias = "documentation_url")]
    pub documentation_url: Option<String>, // not required

    #[serde(skip_serializing_if = "Option::is_none", alias = "icon_url")]
    pub icon_url: Option<String>, // not required

    pub name: String, // required, non-empty

    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<AgentProvider>, // not required

    #[serde(
        skip_serializing_if = "Option::is_none",
        alias = "security_requirements"
    )]
    pub security_requirements: Option<Vec<SecurityRequirement>>, // not required

    #[serde(skip_serializing_if = "Option::is_none", alias = "security_schemes")]
    pub security_schemes: Option<HashMap<String, SecurityScheme>>, // not required

    #[serde(skip_serializing_if = "Option::is_none")]
    pub signatures: Option<Vec<AgentCardSignature>>, // not required

    pub skills: Vec<SkillFormat>, // required

    #[serde(alias = "supported_interfaces")]
    pub supported_interfaces: Vec<AgentInterface>, // required, non-empty

    #[serde(default = "agent_current_version")] // required
    pub version: String,
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

#[cfg(feature = "python")]
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

    #[setter]
    pub fn set_skills(&mut self, skills: Vec<Bound<'_, PyAny>>) -> Result<(), AgentConfigError> {
        let mut parsed_skills = Vec::new();
        for skill in skills {
            if skill.is_instance_of::<AgentSkillStandard>() {
                let standard_skill = skill.extract::<AgentSkillStandard>()?;
                parsed_skills.push(SkillFormat::Standard(standard_skill));
            } else if skill.is_instance_of::<AgentSkill>() {
                let a2a_skill = skill.extract::<AgentSkill>()?;
                parsed_skills.push(SkillFormat::A2A(a2a_skill));
            } else {
                return Err(AgentConfigError::InvalidSkillFormat);
            }
        }
        self.skills = parsed_skills;
        Ok(())
    }

    #[getter]
    pub fn capabilities(&self) -> AgentCapabilities {
        self.capabilities.clone()
    }

    #[setter]
    pub fn set_capabilities(&mut self, val: AgentCapabilities) {
        self.capabilities = val;
    }

    #[getter]
    pub fn default_output_modes(&self) -> Vec<String> {
        self.default_output_modes.clone()
    }

    #[setter]
    pub fn set_default_output_modes(&mut self, val: Vec<String>) {
        self.default_output_modes = val;
    }

    #[getter]
    pub fn default_input_modes(&self) -> Vec<String> {
        self.default_input_modes.clone()
    }

    #[setter]
    pub fn set_default_input_modes(&mut self, val: Vec<String>) {
        self.default_input_modes = val;
    }

    #[getter]
    pub fn description(&self) -> String {
        self.description.clone()
    }

    #[setter]
    pub fn set_description(&mut self, val: String) {
        self.description = val;
    }

    #[getter]
    pub fn documentation_url(&self) -> Option<String> {
        self.documentation_url.clone()
    }

    #[setter]
    pub fn set_documentation_url(&mut self, val: Option<String>) {
        self.documentation_url = val;
    }

    #[getter]
    pub fn icon_url(&self) -> Option<String> {
        self.icon_url.clone()
    }

    #[setter]
    pub fn set_icon_url(&mut self, val: Option<String>) {
        self.icon_url = val;
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn provider(&self) -> Option<AgentProvider> {
        self.provider.clone()
    }

    #[setter]
    pub fn set_provider(&mut self, val: Option<AgentProvider>) {
        self.provider = val;
    }

    #[getter]
    pub fn security_requirements(&self) -> Option<Vec<SecurityRequirement>> {
        self.security_requirements.clone()
    }

    #[setter]
    pub fn set_security_requirements(&mut self, val: Option<Vec<SecurityRequirement>>) {
        self.security_requirements = val;
    }

    #[getter]
    pub fn security_schemes(&self) -> Option<HashMap<String, SecurityScheme>> {
        self.security_schemes.clone()
    }

    #[setter]
    pub fn set_security_schemes(&mut self, val: Option<HashMap<String, SecurityScheme>>) {
        self.security_schemes = val;
    }

    #[getter]
    pub fn signatures(&self) -> Option<Vec<AgentCardSignature>> {
        self.signatures.clone()
    }

    #[setter]
    pub fn set_signatures(&mut self, val: Option<Vec<AgentCardSignature>>) {
        self.signatures = val;
    }

    #[getter]
    pub fn supported_interfaces(&self) -> Vec<AgentInterface> {
        self.supported_interfaces.clone()
    }

    #[setter]
    pub fn set_supported_interfaces(&mut self, val: Vec<AgentInterface>) {
        self.supported_interfaces = val;
    }

    #[getter]
    pub fn version(&self) -> String {
        self.version.clone()
    }

    #[setter]
    pub fn set_version(&mut self, val: String) {
        self.version = val;
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

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

    fn skill_with_skill_md(dir: &std::path::Path, name: &str) -> AgentSkillStandard {
        let skill_dir = dir.join("skills").join(name);
        std::fs::create_dir_all(&skill_dir).unwrap();
        std::fs::write(skill_dir.join("SKILL.md"), "# skill").unwrap();
        AgentSkillStandard {
            name: name.to_string(),
            description: "A valid description.".to_string(),
            license: None,
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: None,
            body: None,
        }
    }

    #[test]
    fn test_validate_name_empty() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = "".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldNameEmpty)
        ));
    }

    #[test]
    fn test_validate_name_too_long() {
        let tmp = tempdir().unwrap();
        let long_name = "a".repeat(65);
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = long_name;
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldNameTooLong { .. })
        ));
    }

    #[test]
    fn test_validate_name_uppercase() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = "MySkill".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::SkillMustBeLowercase { .. })
        ));
    }

    #[test]
    fn test_validate_name_leading_hyphen() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = "-foo".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::SkillNameInvalid { .. })
        ));
    }

    #[test]
    fn test_validate_name_trailing_hyphen() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = "foo-".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::SkillNameInvalid { .. })
        ));
    }

    #[test]
    fn test_validate_name_consecutive_hyphens() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.name = "foo--bar".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::SkillNameInvalid { .. })
        ));
    }

    #[test]
    fn test_validate_name_valid() {
        let tmp = tempdir().unwrap();
        let skill = skill_with_skill_md(tmp.path(), "my-skill-1");
        assert!(skill.validate(tmp.path()).is_ok());
    }

    #[test]
    fn test_validate_description_empty() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.description = "".to_string();
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldDescriptionEmpty)
        ));
    }

    #[test]
    fn test_validate_description_too_long() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.description = "a".repeat(1025);
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldDescriptionTooLong { .. })
        ));
    }

    #[test]
    fn test_validate_description_valid() {
        let tmp = tempdir().unwrap();
        let skill = skill_with_skill_md(tmp.path(), "my-skill");
        assert!(skill.validate(tmp.path()).is_ok());
    }

    #[test]
    fn test_validate_compatibility_empty() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.compatibility = Some("".to_string());
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldCompatibilityEmpty)
        ));
    }

    #[test]
    fn test_validate_compatibility_too_long() {
        let tmp = tempdir().unwrap();
        let mut skill = skill_with_skill_md(tmp.path(), "my-skill");
        skill.compatibility = Some("a".repeat(501));
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::FieldCompatibilityTooLong { .. })
        ));
    }

    #[test]
    fn test_validate_compatibility_none_ok() {
        let tmp = tempdir().unwrap();
        let skill = skill_with_skill_md(tmp.path(), "my-skill");
        assert!(skill.validate(tmp.path()).is_ok());
    }

    #[test]
    fn test_validate_skills_path_not_found() {
        let tmp = tempdir().unwrap();
        let skill = AgentSkillStandard {
            name: "my-skill".to_string(),
            description: "desc".to_string(),
            license: None,
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: None,
            body: None,
        };
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::SkillFileNotFound { .. })
        ));
    }

    #[test]
    fn test_validate_skills_path_last_dir_mismatch() {
        let tmp = tempdir().unwrap();
        let wrong_dir = tmp.path().join("wrong-name");
        std::fs::create_dir_all(&wrong_dir).unwrap();
        std::fs::write(wrong_dir.join("SKILL.md"), "# skill").unwrap();
        let skill = AgentSkillStandard {
            name: "my-skill".to_string(),
            description: "desc".to_string(),
            license: None,
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: Some(wrong_dir.clone()),
            body: None,
        };
        assert!(matches!(
            skill.validate(tmp.path()),
            Err(AgentConfigError::LastDirectoryMustMatchSkillName { .. })
        ));
    }

    #[test]
    fn test_validate_skills_path_happy_path() {
        let tmp = tempdir().unwrap();
        let skill = skill_with_skill_md(tmp.path(), "my-skill");
        assert!(skill.validate(tmp.path()).is_ok());
    }

    fn make_agent_spec(supported_interfaces: Vec<AgentInterface>) -> AgentSpec {
        AgentSpec {
            name: "test-agent".to_string(),
            description: "desc".to_string(),
            version: "0.0.0".to_string(),
            supported_interfaces,
            capabilities: AgentCapabilities::new(false, false, false, None),
            default_input_modes: vec![],
            default_output_modes: vec![],
            skills: vec![],
            provider: None,
            documentation_url: None,
            icon_url: None,
            security_schemes: None,
            security_requirements: None,
            signatures: None,
        }
    }

    #[test]
    fn test_agent_spec_validate_non_empty_interfaces_passes() {
        let tmp = tempdir().unwrap();
        let iface = AgentInterface {
            url: "https://example.com".to_string(),
            protocol_binding: ProtocolBinding::HttpJson,
            protocol_version: "0.3.0".to_string(),
            tenant: String::new(),
        };
        let mut spec = make_agent_spec(vec![iface]);
        assert!(spec.validate(tmp.path(), &None).is_ok());
    }

    #[test]
    fn test_agent_spec_validate_empty_interfaces_no_deploy_config() {
        let tmp = tempdir().unwrap();
        let mut spec = make_agent_spec(vec![]);
        assert!(matches!(
            spec.validate(tmp.path(), &None),
            Err(AgentConfigError::InterfaceUrlMissing)
        ));
    }

    #[test]
    fn test_agent_spec_validate_empty_interfaces_deploy_config_no_urls() {
        let tmp = tempdir().unwrap();
        let mut spec = make_agent_spec(vec![]);
        let deploy = Some(vec![DeploymentConfig {
            environment: "prod".to_string(),
            provider: None,
            location: None,
            urls: vec![],
            resources: None,
            links: None,
            healthcheck: None,
        }]);
        assert!(matches!(
            spec.validate(tmp.path(), &deploy),
            Err(AgentConfigError::InterfaceUrlMissing)
        ));
    }

    #[test]
    fn test_agent_spec_validate_empty_interfaces_populated_from_deploy_config() {
        let tmp = tempdir().unwrap();
        let mut spec = make_agent_spec(vec![]);
        let deploy = Some(vec![DeploymentConfig {
            environment: "prod".to_string(),
            provider: None,
            location: None,
            urls: vec!["https://example.com".to_string()],
            resources: None,
            links: None,
            healthcheck: None,
        }]);
        assert!(spec.validate(tmp.path(), &deploy).is_ok());
        assert_eq!(spec.supported_interfaces.len(), 1);
        assert_eq!(
            spec.supported_interfaces[0].protocol_binding,
            ProtocolBinding::HttpJson
        );
    }

    #[test]
    fn test_protocol_binding_from_str() {
        assert_eq!(ProtocolBinding::from("JSONRPC"), ProtocolBinding::JsonRpc);
        assert_eq!(
            ProtocolBinding::from("HTTP_JSON"),
            ProtocolBinding::HttpJson
        );
        assert_eq!(
            ProtocolBinding::from("HTTP+JSON"),
            ProtocolBinding::HttpJson
        );
        assert_eq!(ProtocolBinding::from("GRPC"), ProtocolBinding::Grpc);
        assert_eq!(ProtocolBinding::from("unknown"), ProtocolBinding::HttpJson);
    }

    #[test]
    fn test_protocol_binding_http_json_serialization() {
        assert_eq!(
            serde_json::to_string(&ProtocolBinding::HttpJson).unwrap(),
            "\"HTTP+JSON\""
        );
    }

    #[test]
    fn test_protocol_binding_http_json_backwards_compat_deserialization() {
        assert_eq!(
            serde_json::from_str::<ProtocolBinding>("\"HTTPJSON\"").unwrap(),
            ProtocolBinding::HttpJson
        );
    }
}
