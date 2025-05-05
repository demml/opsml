use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum OnnxError {
    #[error("{0}")]
    Error(String),

    #[error("Failed to create onnx session - {0}")]
    SessionCreateError(ort::Error),

    #[error("Failed to commit onnx session - {0}")]
    SessionCommitError(ort::Error),

    #[error("Failed to serialize py error - {0}")]
    PySerializeError(pyo3::PyErr),

    #[error("Failed to extract model bytes - {0}")]
    PyModelBytesExtractError(pyo3::PyErr),
}

impl From<OnnxError> for PyErr {
    fn from(err: OnnxError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for OnnxError {
    fn from(err: PyErr) -> Self {
        OnnxError::Error(err.to_string())
    }
}
