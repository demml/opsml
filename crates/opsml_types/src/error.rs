use opsml_crypt::error::CryptError;
use opsml_utils::error::PyUtilError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum TypeError {
    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error("Invalid RegistryType")]
    InvalidRegistryType,

    #[error("Invalid type")]
    InvalidType,

    #[error("Key not found")]
    MissingKeyError,

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Metric not found: {0}")]
    NotMetricFoundError(String),

    #[error("Invalid response type")]
    InvalidResponseError,

    #[error("{0}")]
    PyError(String),

    #[error("MCP server not found")]
    McpServerNotFound(String),

    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,

    #[error("Missing MCP configuration for MCP service type")]
    MissingMCPConfig,

    #[error(transparent)]
    PyUtilError(#[from] PyUtilError),

    #[error("Either space/name or uid must be provided")]
    MissingServiceCardArgsError,
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for TypeError {
    fn from(err: PyErr) -> TypeError {
        TypeError::PyError(err.to_string())
    }
}
