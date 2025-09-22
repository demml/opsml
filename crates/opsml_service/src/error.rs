use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,

    #[error("Missing MCP configuration for MCP service type")]
    MissingMCPConfig,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    YamlError(#[from] serde_yaml::Error),

    #[error("Failed to read service yml file")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to get current directory")]
    CurrentDirError(#[source] std::io::Error),

    #[error("No file name {0} in current directory or any parent directory")]
    MissingServiceFile(String),
}
