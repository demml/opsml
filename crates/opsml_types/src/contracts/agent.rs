use pyo3::prelude::*;
use pythonize::depythonize;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

use crate::error::TypeError;

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
        let depythonized = params.map(|p| depythonize(p).unwrap_or_default());
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
    pub fn new(scheme: &Bound<'_, PyAny>) -> Result<Self, TypeError> {
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
            Err(TypeError::PyError(format!(
                "Unsupported security scheme type: {:?}",
                scheme.get_type()
            )))
        }
    }
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
