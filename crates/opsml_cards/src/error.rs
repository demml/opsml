use std::path::PathBuf;

use opsml_crypt::error::CryptError;
use opsml_interfaces::error::{DataInterfaceError, ModelInterfaceError};
use opsml_state::error::StateError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::TypeError;
use opsml_types::RegistryType;
use opsml_utils::error::{PyUtilError, UtilError};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use scouter_client::DriftType;
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
    PyUtilError(#[from] PyUtilError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    ProfileError(#[from] scouter_client::ProfileError),

    #[error(transparent)]
    DriftError(#[from] scouter_client::DriftError),

    #[error("{0}")]
    CustomError(String),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Interface must be an instance of ModelInterface")]
    MustBeModelInterfaceError,

    #[error("Interface must be an instance of DataInterface")]
    MustBeDataInterfaceError,

    #[error("Interface not found")]
    InterfaceNotFoundError,

    #[error("Model has not been set. Load the model and retry")]
    ModelNotSetError,

    #[error("Data has not been set. Load the data and retry")]
    DataNotSetError,

    #[error("Alias not found in ServiceCard")]
    AliasNotFoundInDeckError,

    #[error("File not found for file: {0}")]
    FileNotFoundError(PathBuf),

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

    #[error("Failed to convert into string")]
    IntoStringError,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Failed to get attribute {0}. Has this card been registered?")]
    MissingAttributeError(String),

    #[error("Registry type is required")]
    MissingRegistryTypeError,

    #[error("Either space/name or uid must be provided")]
    MissingServiceCardArgsError,

    #[error("Index out of bounds: {0}")]
    IndexOutOfBoundsError(usize),

    #[error("KeyError: key {0} not found in ServiceCard")]
    ServiceCardKeyError(String),

    #[error("Path does not exist: {0}")]
    PathDoesNotExistError(String),

    #[error("Unsupported registry type: {0}")]
    UnsupportedRegistryTypeError(RegistryType),

    #[error("Failed to get drift profile")]
    DriftProfileNotFoundError,

    #[error("Unsupported drift type: {0}")]
    UnsupportedDriftType(DriftType),
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
