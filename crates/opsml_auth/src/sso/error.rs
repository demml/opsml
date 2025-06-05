use thiserror::Error;

#[derive(Error, Debug)]
pub enum SsoError {
    #[error("Environment variable not set")]
    EnvVarNotSet,

    #[error("Invalid SSO provider specified: {0}")]
    InvalidProvider(String),
}
