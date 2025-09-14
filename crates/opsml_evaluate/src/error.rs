use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum EvaluationError {
    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

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

impl<'a> From<pyo3::DowncastError<'a, 'a>> for EvaluationError {
    fn from(err: pyo3::DowncastError) -> Self {
        EvaluationError::DowncastError(err.to_string())
    }
}
