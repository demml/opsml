use pyo3::PyErr;
use pyo3::exceptions::PyRuntimeError;
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

    #[error("{0}")]
    PyError(String),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Invalid number")]
    InvalidNumber,

    #[error("Root must be an object")]
    RootMustBeObjectError,

    #[error("Failed to check if the context is a Pydantic BaseModel. Error: {0}")]
    FailedToCheckPydanticModel(String),

    #[error("Failed to import pydantic module. Error: {0}")]
    FailedToImportPydantic(String),

    #[error("Failed to extract python type")]
    FailedToExtract,
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for UtilError {
    fn from(err: pyo3::CastError) -> Self {
        UtilError::DowncastError(err.to_string())
    }
}

impl From<UtilError> for PyErr {
    fn from(err: UtilError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for UtilError {
    fn from(err: PyErr) -> UtilError {
        UtilError::PyError(err.to_string())
    }
}
