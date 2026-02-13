use crate::types::{DownloadEvent, ReloadEvent};
use opsml_cards::error::CardError;
use opsml_registry::error::RegistryError;
use opsml_types::error::TypeError;
use pyo3::PyErr;
use pyo3::pyclass::PyClassGuardError;
use scouter_client::PyEventError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("{0}")]
    Error(String),

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

    #[error("Poison error occurred")]
    PoisonError(String),

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

    #[error(transparent)]
    StorageError(#[from] opsml_storage::StorageError),

    #[error("Failed to downcast")]
    DowncastError(String),

    #[error(transparent)]
    EventError(#[from] scouter_client::EventError),

    #[error(transparent)]
    DownloadEventError(#[from] tokio::sync::mpsc::error::SendError<DownloadEvent>),

    #[error("Failed to acquire lock")]
    LockError,

    #[error("Failed to start download loop")]
    DownloadLoopFailedToStartError,

    #[error("Failed to start reload loop")]
    ReloadLoopFailedToStartError,

    #[error(transparent)]
    JoinError(#[from] tokio::task::JoinError),

    #[error("No download channel found")]
    NoDownloadTxError,

    #[error("No reload channel found")]
    NoReloadTxError,

    #[error("Failed to acquire lock on ScouterQueue")]
    ScouterQueueLockError(String),

    #[error("Failed to start download task")]
    DownloadTaskFailedToStartError,

    #[error("Failed to start reload task")]
    ReloadTaskFailedToStartError,

    #[error("{0}")]
    ScouterQueueRuntimeError(String),
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for AppError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        AppError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for AppError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        AppError::DowncastError(err.to_string())
    }
}

impl From<PyErr> for AppError {
    fn from(err: PyErr) -> Self {
        AppError::Error(err.to_string())
    }
}

impl From<AppError> for PyErr {
    fn from(err: AppError) -> PyErr {
        let msg = err.to_string();
        pyo3::exceptions::PyRuntimeError::new_err(msg)
    }
}
