use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum LLMError {
    #[error("{0}")]
    PyErr(String),
}

impl From<LLMError> for PyErr {
    fn from(err: LLMError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for LLMError {
    fn from(err: PyErr) -> LLMError {
        LLMError::PyErr(err.to_string())
    }
}
