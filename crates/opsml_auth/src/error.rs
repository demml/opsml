use thiserror::Error;

#[derive(Error, Debug)]
pub enum AuthError {
    #[error("Invalid username provided")]
    InvalidUser,

    #[error("Invalid password provided")]
    InvalidPassword,

    #[error("Session timeout for user occured")]
    SessionTimeout,

    #[error("JWT token provided is invalid")]
    InvalidJwtToken,

    #[error("Refresh token is invalid")]
    InvalidRefreshToken,

    #[error("Error creating JWT token")]
    JWTError,

    #[error("Invalid recovery code provided")]
    InvalidRecoveryCode,

    #[error("No SSO provider configured")]
    SsoProviderNotSet,

    #[error("Failed to hash: {0}")]
    HashingError(String),
}
