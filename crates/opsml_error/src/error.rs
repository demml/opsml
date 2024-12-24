use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::PyErr;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SettingsError {
    #[error("Settings Error: {0}")]
    Error(String),
}

impl From<SettingsError> for PyErr {
    fn from(err: SettingsError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("Storage Error: {0}")]
    Error(String),
}

impl From<StorageError> for PyErr {
    fn from(err: StorageError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Api Error: {0}")]
    Error(String),
}

impl From<ApiError> for PyErr {
    fn from(err: ApiError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum UtilError {
    #[error("Util Error: {0}")]
    Error(String),

    #[error("Failed to validate uuid")]
    UuidError,

    #[error("Failed to parse date")]
    DateError,

    #[error("Failed to find file")]
    FileNotFoundError,
}

impl From<UtilError> for PyErr {
    fn from(err: UtilError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum TypeError {
    #[error("Type Error: {0}")]
    Error(String),

    #[error("Error serializing data")]
    SerializationError,

    #[error("Error creating path")]
    CreatePathError,

    #[error("Error getting parent path")]
    GetParentPathError,

    #[error("Failed to create directory")]
    CreateDirectoryError,

    #[error("Failed to write to file")]
    WriteError,

    #[error("Failed to parse date")]
    DateError,

    #[error("Error reading file entry")]
    FileEntryError,

    #[error("File not found")]
    FileNotFoundError,
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum LoggingError {
    #[error("Logging Error: {0}")]
    Error(String),
}

impl From<LoggingError> for PyErr {
    fn from(err: LoggingError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug, Serialize, Deserialize)]
pub enum ServerError {
    #[error("Failed to delete file: {0}")]
    DeleteError(String),

    #[error("Failed to create multipart: {0}")]
    MultipartError(String),

    #[error("Failed to presign: {0}")]
    PresignedError(String),

    #[error("Failed to list files: {0}")]
    ListFileError(String),
}

#[derive(Error, Debug)]
pub enum SqlError {
    #[error("Failed to run sql migrations: {0}")]
    MigrationError(String),

    #[error("Failed to run sql query: {0}")]
    QueryError(String),

    #[error("Failed to parse version: {0}")]
    VersionError(String),

    #[error("File error: {0}")]
    FileError(String),

    #[error("Error - {0}")]
    GeneralError(String),

    #[error("Failed to connect to the database - {0}")]
    ConnectionError(String),
}

#[derive(Error, Debug)]
pub enum VersionError {
    #[error("SemVer failed: {0}")]
    SemVerError(String),

    #[error("Invalid version: {0}")]
    InvalidVersion(String),

    #[error("Invalid pre release: {0}")]
    InvalidPreRelease(String),

    #[error("Invalid build: {0}")]
    InvalidBuild(String),
}

#[derive(Error, Debug)]
pub enum AuthError {
    #[error("Invalid username provided")]
    InvalidUser,

    #[error("Invalid password provided")]
    InvalidPassword,

    #[error("Session timeout for user occured")]
    SessionTimeout,

    #[error("JWT token provided is invalid")]
    InvalidJwtToken,

    #[error("Refresh token is invalid")]
    InvalidRefreshToken,
}

#[derive(Error, Debug)]
pub enum RegistryError {
    #[error("Failed to initialize registry - {0}")]
    NewError(String),

    #[error("{0}")]
    Error(String),

    #[error("Failed to list cards - {0}")]
    ListCardsError(String),
}

impl From<RegistryError> for PyErr {
    fn from(err: RegistryError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum CardError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error(transparent)]
    StorageError(#[from] StorageError),
}

impl From<CardError> for PyErr {
    fn from(err: CardError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum SaveError {
    #[error("{0}")]
    Error(String),
}

impl From<SaveError> for PyErr {
    fn from(err: SaveError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

create_exception!(opsml_error, OpsmlError, PyException);
