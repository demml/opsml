use pyo3::{IntoPyObjectExt, prelude::*};
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

    #[getter]
    pub fn get_params<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, TypeError> {
        match &self.params {
            Some(params) => Ok(pythonize::pythonize(py, params)?),
            None => Ok(py.None().into_bound_py_any(py)?),
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct HttpAuthSecurityScheme {
    #[pyo3(get, set)]
    scheme: String,
    #[pyo3(get, set)]
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

#[pyclass]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct Oauth2SecurityScheme {
    #[pyo3(get, set)]
    pub description: Option<String>,
    #[pyo3(get, set)]
    pub flows: OAuthFlows,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct OpenIdConnectSecurityScheme {
    #[pyo3(get, set)]
    pub description: Option<String>,
    #[pyo3(get, set)]
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

#[pyclass]
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
    #[pyo3(get, set)]
    pub authorization_code: Option<AuthorizationCodeFlow>,
    #[pyo3(get, set)]
    pub client_credentials: Option<ClientCredentialsFlow>,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AuthorizationCodeFlow {
    #[pyo3(get, set)]
    pub authorization_url: String,
    #[pyo3(get, set)]
    pub pkce_required: bool,
    #[pyo3(get, set)]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ClientCredentialsFlow {
    #[pyo3(get, set)]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct DeviceCodeFlow {
    #[pyo3(get, set)]
    pub device_authorization_url: String,
    #[pyo3(get, set)]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ImplicitAuthFlow {
    #[pyo3(get, set)]
    pub authorization_url: String,
    #[pyo3(get, set)]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct PassWordAuthFlow {
    #[pyo3(get, set)]
    pub refresh_url: String,
    #[pyo3(get, set)]
    pub scopes: HashMap<String, String>,
    #[pyo3(get, set)]
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

#[pyclass]
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct AgentSpec {
    #[pyo3(get, set)]
    pub capabilities: AgentCapabilities,

    #[pyo3(get, set)]
    #[serde(alias = "default_output_modes")]
    pub default_output_modes: Vec<String>,

    #[pyo3(get, set)]
    #[serde(alias = "default_input_modes")]
    pub default_input_modes: Vec<String>,

    #[pyo3(get, set)]
    pub description: String,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "documentation_url")]
    pub documentation_url: Option<String>,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "icon_url")]
    pub icon_url: Option<String>,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<AgentProvider>,

    #[pyo3(get, set)]
    #[serde(
        skip_serializing_if = "Option::is_none",
        alias = "security_requirements"
    )]
    pub security_requirements: Option<Vec<SecurityRequirement>>,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none", alias = "security_schemes")]
    pub security_schemes: Option<HashMap<String, SecurityScheme>>,

    #[pyo3(get, set)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signatures: Option<Vec<AgentCardSignature>>,

    #[pyo3(get, set)]
    pub skills: Vec<AgentSkill>,

    #[pyo3(get, set)]
    #[serde(alias = "supported_interfaces")]
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
