use thiserror::Error;

#[derive(Error, Debug)]
pub enum SsoError {
    #[error("Environment variable not set")]
    EnvVarNotSet,

    #[error("Failed to parse Keycloak settings from environment variables")]
    KeycloakEnvVarError(#[from] std::env::VarError),

    #[error("Invalid SSO provider specified: {0}")]
    InvalidProvider(String),

    #[error("Account error: {0}")]
    AccountNotConfigured(String),

    #[error("Authentication failed: {0}")]
    AuthenticationFailed(String),

    #[error("Request failed")]
    ReqwestError(#[from] reqwest::Error),

    #[error("Request failed: {0}")]
    FallbackError(String),

    #[error("Unauthorized access")]
    Unauthorized,

    #[error("JWT decode error")]
    JwtDecodeError(#[from] jsonwebtoken::errors::Error),
}
