use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use reqwest::StatusCode;
use serde::Deserialize;
use thiserror::Error;
use tracing::error;
#[derive(Error, Debug, Deserialize)]
pub enum PotatoError {
    #[error("Error: {0}")]
    Error(String),

    #[error("Missing API Key")]
    MissingAPIKey,

    #[error("Failed to serialize string")]
    SerializeError,

    #[error("Failed to deserialize string")]
    DeSerializeError,

    #[error("Failed to create path")]
    CreatePathError,

    #[error("Failed to get parent path")]
    GetParentPathError,

    #[error("Failed to create directory")]
    CreateDirectoryError,

    #[error("Failed to write to file")]
    WriteError,

    #[error("Unsupported interaction type")]
    UnsupportedInteractionType,

    #[error("Sanitization error: {0}")]
    SanitizationError(String),
}

impl From<PotatoError> for PyErr {
    fn from(err: PotatoError) -> PyErr {
        PyErr::new::<PotatoHeadError, _>(err.to_string())
    }
}

impl From<PyErr> for PotatoError {
    fn from(err: PyErr) -> Self {
        PotatoError::Error(err.to_string())
    }
}

create_exception!(potato_head, PotatoHeadError, PyException);

#[derive(Error, Debug)]
pub enum AgentError {
    #[error("Failed to create header value for the agent client")]
    CreateHeaderValueError(#[from] reqwest::header::InvalidHeaderValue),

    #[error("Failed to create header name for the agent client")]
    CreateHeaderNameError(#[from] reqwest::header::InvalidHeaderName),

    #[error("Failed to create agent client")]
    CreateClientError(#[source] reqwest::Error),

    #[error("Request failed")]
    RequestError(#[from] reqwest::Error),

    #[error("Failed to serialize chat request")]
    SerializationError(#[from] serde_json::Error),

    #[error("Failed to get chat completion response: {0}")]
    ChatCompletionError(StatusCode),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Failed to get environment variable: {0}")]
    EnvVarError(#[from] std::env::VarError),

    #[error("Failed to extract client: {0}")]
    ClientExtractionError(String),

    #[error(transparent)]
    PyError(#[from] pyo3::PyErr),

    #[error("Client did not provide response")]
    ClientNoResponseError,

    #[error("No ready tasks found but pending tasks remain. Possible circular dependency.")]
    NoTaskFoundError,
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for AgentError {
    fn from(err: pyo3::DowncastError) -> Self {
        AgentError::DowncastError(err.to_string())
    }
}

impl From<AgentError> for PyErr {
    fn from(err: AgentError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
