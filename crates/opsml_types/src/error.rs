use opsml_crypt::error::CryptError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum TypeError {
    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error("Invalid RegistryType")]
    InvalidRegistryType,

    #[error("Invalid type")]
    InvalidType,

    #[error("Key not found")]
    MissingKeyError,

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),
}

#[derive(Error, Debug)]
pub enum PyTypeError {
    #[error(transparent)]
    TypeError(#[from] TypeError),
}

impl From<PyTypeError> for PyErr {
    fn from(err: PyTypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
