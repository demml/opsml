use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;
#[derive(Error, Debug)]
pub enum ServiceError {
    #[error(
        r#"
Missing deployment configuration for MCP service {0}.
Check the 'deploy' section of the spec and ensure at least one deployment
configuration environment matches the current environment set in APP_ENV.
"#
    )]
    MissingDeploymentConfigForMCPService(String),

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

impl From<ServiceError> for PyErr {
    fn from(err: ServiceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
