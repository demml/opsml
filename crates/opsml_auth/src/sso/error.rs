use thiserror::Error;

#[derive(Error, Debug)]
pub enum SsoError {
    #[error("Environment variable not set: {0}")]
    EnvVarNotSet(String),

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

    #[error("Bad request: {0}")]
    BadRequest(String),

    #[error("Missing public key for SSO provider")]
    MissingPublicKey,

    #[error("Failed to fetch JWK: {0}")]
    FailedToFetchJwk(String),

    #[error("Missing signing key for SSO provider")]
    MissingSigningKey,

    #[error("JWT decode error: {0}")]
    JwtDecodeError(#[from] jsonwebtoken::errors::Error),
}
