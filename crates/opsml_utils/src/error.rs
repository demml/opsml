use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum UtilError {
    #[error("Failed to validate uuid")]
    UuidError,

    #[error("Failed to parse date")]
    DateError,

    #[error("Failed to find file")]
    FileNotFoundError,

    #[error("Error serializing data")]
    SerializationError,

    #[error("Error getting parent path")]
    GetParentPathError,

    #[error("Failed to create directory")]
    CreateDirectoryError,

    #[error("Failed to write to file")]
    WriteError,

    #[error("Failed to read to file")]
    ReadError,

    #[error("Invalid space/name pattern")]
    InvalidSpaceNamePattern,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    WalkError(#[from] walkdir::Error),

    #[error("File path not found")]
    FilePathNotFoundError,

    #[error(transparent)]
    RegexError(#[from] regex::Error),

    #[error("Space/name pattern is too long")]
    SpaceNamePatternTooLong,
}

#[derive(Error, Debug)]
pub enum PyUtilError {
    #[error("{0}")]
    PyError(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Invalid number")]
    InvalidNumber,

    #[error("Root must be an object")]
    RootMustBeObjectError,
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for PyUtilError {
    fn from(err: pyo3::DowncastError) -> Self {
        PyUtilError::DowncastError(err.to_string())
    }
}

impl From<PyUtilError> for PyErr {
    fn from(err: PyUtilError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for PyUtilError {
    fn from(err: PyErr) -> PyUtilError {
        PyUtilError::PyError(err.to_string())
    }
}
