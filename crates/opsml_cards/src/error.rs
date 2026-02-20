use opsml_crypt::error::CryptError;
use opsml_interfaces::error::{DataInterfaceError, ModelInterfaceError};
use opsml_state::error::StateError;
use opsml_storage::storage::error::StorageError;
use opsml_types::RegistryType;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::pyclass::PyClassGuardError;
use scouter_client::DriftType;
use std::path::PathBuf;
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
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    ProfileError(#[from] scouter_client::ProfileError),

    #[error(transparent)]
    DriftError(#[from] scouter_client::DriftError),

    #[error("{0}")]
    Error(String),

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

    #[error("Index out of bounds: {0}")]
    IndexOutOfBoundsError(usize),

    #[error("KeyError: key {0} not found in ServiceCard")]
    ServiceCardKeyError(String),

    #[error("Path does not exist: {0}")]
    PathDoesNotExistError(String),

    #[error("Unsupported registry type: {0}")]
    UnsupportedRegistryTypeError(RegistryType),

    #[error("Failed to to get drift profile from card profile map")]
    DriftProfileNotFoundInMap,

    #[error("Unsupported drift type: {0}")]
    UnsupportedDriftType(DriftType),

    #[error(transparent)]
    ServiceError(#[from] opsml_service::error::ServiceError),

    #[error(transparent)]
    SerdeYamlError(#[from] serde_yaml::Error),
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for CardError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        CardError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for CardError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        CardError::DowncastError(err.to_string())
    }
}

impl From<PyErr> for CardError {
    fn from(err: PyErr) -> Self {
        CardError::Error(err.to_string())
    }
}

impl From<CardError> for PyErr {
    fn from(err: CardError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
