use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum EvaluationError {
    #[error("{0}")]
    PyError(String),

    #[error("{0}")]
    DowncastError(String),

    #[error(transparent)]
    EvalError(#[from] scouter_client::EvaluationError),
}

impl From<EvaluationError> for PyErr {
    fn from(err: EvaluationError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for EvaluationError {
    fn from(err: PyErr) -> EvaluationError {
        EvaluationError::PyError(err.to_string())
    }
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for EvaluationError {
    fn from(err: pyo3::DowncastError) -> Self {
        EvaluationError::DowncastError(err.to_string())
    }
}
