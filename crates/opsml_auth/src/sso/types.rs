use crate::sso::error::SsoError;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize)]
pub struct KeyCloakSettings {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
    pub auth_server_url: String,
}

#[derive(Deserialize, Debug)]
pub struct KeycloakTokenResponse {
    pub access_token: String,
    pub expires_in: u64,
    pub refresh_token: String,
    pub refresh_expires_in: u64,
    pub token_type: String,
    pub not_before_policy: u64,
    pub session_state: String,
    pub scope: String,
}

#[derive(Deserialize, Debug)]
pub struct KeycloakUserInfo {
    pub name: String,
    pub preferred_username: String,
    pub email: Option<String>,
}

pub enum SsoProvider {
    Google,
    Microsoft,
    GitHub,
    Keycloak,
}

impl SsoProvider {
    pub fn as_str(&self) -> &str {
        match self {
            SsoProvider::Google => "google",
            SsoProvider::Microsoft => "microsoft",
            SsoProvider::GitHub => "github",
            SsoProvider::Keycloak => "keycloak",
        }
    }

    pub fn from_env() -> Result<Self, SsoError> {
        match std::env::var("SSO_PROVIDER")
            .map_err(|_| SsoError::EnvVarNotSet)?
            .to_lowercase()
            .as_str()
        {
            "google" => Ok(SsoProvider::Google),
            "microsoft" => Ok(SsoProvider::Microsoft),
            "github" => Ok(SsoProvider::GitHub),
            "keycloak" => Ok(SsoProvider::Keycloak),
            _ => Err(SsoError::InvalidProvider(
                std::env::var("SSO_PROVIDER").unwrap_or_default(),
            )),
        }
    }

    pub fn is_enabled() -> bool {
        std::env::var("SSO_ENABLED")
            .map(|val| val.to_lowercase() == "true")
            .unwrap_or(false)
    }
}
