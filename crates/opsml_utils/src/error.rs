use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use serde::{Deserialize, Serialize};
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

    #[error("Failed to create regex")]
    RegexError,

    #[error("Invalid space/name pattern")]
    InvalidSpaceNamePattern,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    WalkError(#[from] walkdir::Error),

    #[error("File path not found")]
    FilePathNotFoundError,
}

impl From<UtilError> for PyErr {
    fn from(err: UtilError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
