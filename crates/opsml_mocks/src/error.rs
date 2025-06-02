use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TestServerError {
    #[error("Failed to find available port")]
    PortNotFound,

    #[error("Failed to start Opsml Server")]
    ServerStartError,

    #[error("Failed to set environment variables for client")]
    SetEnvVarsError,

    #[error("{0}")]
    CustomError(String),
}

impl From<TestServerError> for PyErr {
    fn from(err: TestServerError) -> PyErr {
        let msg = err.to_string();
        PyRuntimeError::new_err(msg)
    }
}
