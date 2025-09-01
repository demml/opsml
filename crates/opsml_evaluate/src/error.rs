use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum EvaluationError {
    #[error("Invalid response type. Expected Score")]
    InvalidResponseError,

    #[error(transparent)]
    WorkflowError(#[from] potato_head::WorkflowError),

    #[error(transparent)]
    PyUtilError(#[from] opsml_utils::error::PyUtilError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error("{0}")]
    DowncastError(String),

    #[error(transparent)]
    JoinError(#[from] tokio::task::JoinError),

    #[error("Missing key: {0}")]
    MissingKeyError(String),
}

impl From<EvaluationError> for PyErr {
    fn from(err: EvaluationError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for EvaluationError {
    fn from(err: pyo3::DowncastError) -> Self {
        EvaluationError::DowncastError(err.to_string())
    }
}
