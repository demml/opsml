use opsml_cards::error::CardError;
use opsml_types::error::TypeError;
use pyo3::PyErr;
use scouter_client::PyEventError;
use thiserror::Error;
use tracing::error;
#[derive(Error, Debug)]
pub enum AppError {
    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    QueueError(#[from] PyEventError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error("No queue set for application")]
    QueueNotFoundError,

    #[error(transparent)]
    CardError(#[from] CardError),
}

impl From<AppError> for PyErr {
    fn from(err: AppError) -> PyErr {
        let msg = err.to_string();
        pyo3::exceptions::PyRuntimeError::new_err(msg)
    }
}
