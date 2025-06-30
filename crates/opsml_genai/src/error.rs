use potato_head::{AgentError, UtilError, WorkflowError};
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use serde_json;
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

#[derive(Error, Debug)]
pub enum PyWorkflowError {
    #[error("Error: {0}")]
    Error(String),

    #[error(transparent)]
    WorkflowError(#[from] WorkflowError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error("Failed to serialize chat request: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Failed to acquire lock on workflow")]
    LockAcquireError,

    #[error("Failed to acquire read lock on workflow")]
    ReadLockAcquireError,
}
impl From<PyWorkflowError> for PyErr {
    fn from(err: PyWorkflowError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for PyWorkflowError {
    fn from(err: PyErr) -> Self {
        PyWorkflowError::Error(err.to_string())
    }
}
