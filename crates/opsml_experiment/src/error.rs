use opsml_cards::error::CardError;
use opsml_crypt::error::CryptError;
use opsml_registry::error::RegistryError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::{PyTypeError, TypeError};
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum ExperimentError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    PyTypeError(#[from] PyTypeError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error("Failed to load experiment card")]
    LoadCardError(#[source] RegistryError),

    #[error("Failed to insert metric")]
    InsertMetricError(#[source] RegistryError),

    #[error("Failed to insert parameter")]
    InsertParameterError(#[source] RegistryError),

    #[error("Path does not exist")]
    PathNotExistError,

    #[error("Path is not a file. Use log_artifacts if you wish to log multiple artifacts")]
    PathNotFileError,
}

impl From<ExperimentError> for PyErr {
    fn from(err: ExperimentError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
