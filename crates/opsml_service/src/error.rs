use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("Missing deployment configuration for MCP service type")]
    MissingDeploymentConfigForMCPService,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    TypeError(#[from] opsml_types::error::TypeError),

    #[error(transparent)]
    YamlError(#[from] serde_yaml::Error),

    #[error("Failed to read service yml file")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to get current directory")]
    CurrentDirError(#[source] std::io::Error),

    #[error("No file name {0} in current directory or any parent directory")]
    MissingServiceFile(String),

    #[error(transparent)]
    StateError(#[from] opsml_state::error::StateError),
}
