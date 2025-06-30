use potato_head::agent::agents::error::AgentError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum PyAgentError {
    #[error("Error: {0}")]
    Error(String),

    #[error(transparent)]
    AgentError(#[from] AgentError),
}

impl From<PyAgentError> for PyErr {
    fn from(err: PyAgentError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for PyAgentError {
    fn from(err: PyErr) -> Self {
        PyAgentError::Error(err.to_string())
    }
}
