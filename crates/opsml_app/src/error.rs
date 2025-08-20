use crate::reloader::ReloadEvent;
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

    #[error(transparent)]
    SendError(#[from] tokio::sync::mpsc::error::SendError<ReloadEvent>),

    #[error("No queue set for application")]
    QueueNotFoundError,

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error("Failed to parse cron schedule for the next run")]
    GetNextRunError,

    #[error("No upcoming schedule found")]
    NoUpcomingSchedule,

    #[error("Failed to signal shutdown")]
    SignalCompletionError,

    #[error("Service card not found")]
    CardNotFound,

    #[error(transparent)]
    InvalidCron(#[from] cron::error::Error),

    #[error("Failed to initialize reloader")]
    FailedToInitializeReloader,

    #[error("Reloader not found")]
    ReloaderNotFound,

    #[error("Reloader is not running")]
    ReloaderNotRunning,

    #[error("Failed to update lock")]
    UpdateLockError,

    #[error("Failed to update service")]
    UpdateServiceError(String),

    #[error("Failed to reload service")]
    ReloadServiceError(String),
}

impl From<AppError> for PyErr {
    fn from(err: AppError) -> PyErr {
        let msg = err.to_string();
        pyo3::exceptions::PyRuntimeError::new_err(msg)
    }
}
