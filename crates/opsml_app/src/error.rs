use opsml_cards::error::CardError;
use opsml_registry::error::RegistryError;
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

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error("No queue set for application")]
    QueueNotFoundError,

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error("Failed to parse cron schedule for the next run")]
    GetNextRunError,

    #[error("Invalid cron schedule")]
    InvalidCronSchedule,
}

impl From<AppError> for PyErr {
    fn from(err: AppError) -> PyErr {
        let msg = err.to_string();
        pyo3::exceptions::PyRuntimeError::new_err(msg)
    }
}
