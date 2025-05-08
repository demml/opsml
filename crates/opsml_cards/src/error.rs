use opsml_crypt::error::CryptError;
use opsml_interfaces::error::{DataInterfaceError, ModelInterfaceError};
use opsml_state::error::StateError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum CardError {
    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    StateError(#[from] StateError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error("{0}")]
    CustomError(String),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Interface must be an instance of ModelInterface")]
    MustBeModelInterfaceError,

    #[error("Interface not found")]
    InterfaceNotFoundError,

    #[error("Model has not been set. Load the model and retry")]
    ModelNotSetError,

    #[error(transparent)]
    DataInterfaceError(#[from] DataInterfaceError),

    #[error(transparent)]
    ModelInterfaceError(#[from] ModelInterfaceError),

    #[error("Decryption key not found")]
    DecryptionKeyNotFoundError,

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    CryptError(#[from] CryptError),
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for CardError {
    fn from(err: pyo3::DowncastError) -> Self {
        CardError::DowncastError(err.to_string())
    }
}

impl From<CardError> for PyErr {
    fn from(err: CardError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
