use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::PyErr;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum PyProjectTomlError {
    #[error("Failed to find absolute path")]
    AbsolutePathError(#[source] std::io::Error),

    // Borrowed from UV
    #[error("No file name {0} in current directory or any parent directory")]
    MissingPyprojectToml(String),

    #[error("Failed to read `pyproject.toml`")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to parse `pyproject.toml`")]
    ParseError(#[from] toml_edit::TomlError),

    #[error("Failed to get current directory")]
    CurrentDirError(#[source] std::io::Error),

    #[error("Failed to deserialize `pyproject.toml`")]
    TomlSchema(#[source] toml_edit::de::Error),

    #[error("Failed to deserialize `opsml.lock`")]
    LockFileSchema(#[source] toml_edit::de::Error),

    #[error("Failed to write opsml.lock file")]
    FailedToLockFile(#[source] std::io::Error),

    #[error("Failed to read opsml.lock file")]
    FailedToReadLockFile(#[source] std::io::Error),

    #[error("Failed to parse opsml.lock file")]
    FailedToParseLockFile(#[source] toml_edit::TomlError),
}

#[derive(Error, Debug)]
pub enum EventError {
    #[error("{0}")]
    Error(String),
}

#[derive(Error, Debug)]
pub enum CliError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    PyProjectTomlError(#[from] PyProjectTomlError),

    #[error("Registry type not found")]
    MissingRegistryType,

    #[error("CardRecord not found in response")]
    MissingCardRecord,

    #[error("Registry type {0} not supported")]
    RegistryTypeNotSupported(String),

    #[error("Cards were not provided as part of the toml app config")]
    MissingDeckCards,

    #[error("CardDeck missing card UIDs")]
    MissingCardDeckUids,

    #[error("Failed to create card deck")]
    CreateDeckError(#[from] CardError),

    #[error("Failed to get current directory")]
    CurrentDirectoryError(#[source] std::io::Error),

    #[error("No tools found in pyproject.toml. An tool config must be present")]
    MissingTools,

    #[error("No apps found in pyproject.toml. An app config must be present")]
    MissingApp,

    #[error("Registry type {0} is not supported for apps")]
    UnsupportedRegistryType(String),
}

impl From<CliError> for PyErr {
    fn from(err: CliError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum SettingsError {
    #[error("Settings Error: {0}")]
    Error(String),
}

impl From<SettingsError> for PyErr {
    fn from(err: SettingsError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("Storage Error: {0}")]
    Error(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    ProgressError(#[from] ProgressError),

    #[error("Unauthorized: {0}")]
    PermissionDenied(String),

    #[error(transparent)]
    StateError(#[from] StateError),
}

impl From<StorageError> for PyErr {
    fn from(err: StorageError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Api Error: {0}")]
    Error(String),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    TypeError(#[from] TypeError),
}

impl From<ApiError> for PyErr {
    fn from(err: ApiError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug, Deserialize, Serialize)]
pub enum UtilError {
    #[error("{0}")]
    Error(String),

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
}

impl From<UtilError> for PyErr {
    fn from(err: UtilError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug, Deserialize, Serialize)]
pub enum TypeError {
    #[error("{0}")]
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

    #[error(transparent)]
    UtilError(#[from] UtilError),
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum LoggingError {
    #[error("Logging Error: {0}")]
    Error(String),
}

impl From<LoggingError> for PyErr {
    fn from(err: LoggingError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
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

    #[error(transparent)]
    SqlError(#[from] SqlError),

    #[error("{0}")]
    Error(String),
}

#[derive(Error, Debug, Serialize, Deserialize)]
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

    #[error(transparent)]
    TypeError(#[from] TypeError),
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

    #[error("Error creating JWT token")]
    JWTError,
}

#[derive(Error, Debug)]
pub enum RegistryError {
    #[error("Failed to initialize registry - {0}")]
    NewError(String),

    #[error("{0}")]
    Forbidden(String),

    #[error("{0}")]
    Error(String),

    #[error("Failed to list cards - {0}")]
    ListCardsError(String),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    ApiError(#[from] ApiError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    SqlError(#[from] SqlError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    StateError(#[from] StateError),

    #[error("Failed to get registry record")]
    FailedToGetRegistryRecordError,
}

impl From<RegistryError> for PyErr {
    fn from(err: RegistryError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
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

    #[error(transparent)]
    CryptError(#[from] CryptError),
}

impl From<CardError> for PyErr {
    fn from(err: CardError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<PyErr> for CardError {
    fn from(err: PyErr) -> Self {
        CardError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum SaveError {
    #[error("{0}")]
    Error(String),
}

impl From<SaveError> for PyErr {
    fn from(err: SaveError) -> PyErr {
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum RunError {
    #[error("{0}")]
    Error(String),
}

impl From<RunError> for PyErr {
    fn from(err: RunError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum OnnxError {
    #[error("{0}")]
    Error(String),
}

impl From<OnnxError> for PyErr {
    fn from(err: OnnxError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<PyErr> for OnnxError {
    fn from(err: PyErr) -> Self {
        OnnxError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum ExperimentError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),
}

impl From<ExperimentError> for PyErr {
    fn from(err: ExperimentError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<PyErr> for ExperimentError {
    fn from(err: PyErr) -> Self {
        ExperimentError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum InterfaceError {
    #[error("{0}")]
    Error(String),
}

impl From<InterfaceError> for PyErr {
    fn from(err: InterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<PyErr> for InterfaceError {
    fn from(err: PyErr) -> Self {
        InterfaceError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum ProgressError {
    #[error("{0}")]
    Error(String),
}

#[derive(Error, Debug)]
pub enum CryptError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    ProgressError(#[from] ProgressError),
}

impl From<CryptError> for PyErr {
    fn from(err: CryptError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<std::io::Error> for CryptError {
    fn from(err: std::io::Error) -> Self {
        CryptError::Error(err.to_string())
    }
}

impl From<PyErr> for CryptError {
    fn from(err: PyErr) -> Self {
        CryptError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum StateError {
    #[error("{0}")]
    Error(String),

    #[error("Failed to read config")]
    ReadConfigError(#[source] std::io::Error),
}

impl From<StateError> for PyErr {
    fn from(err: StateError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        OpsmlError::new_err(err.to_string())
    }
}

impl From<PyErr> for StateError {
    fn from(err: PyErr) -> Self {
        StateError::Error(err.to_string())
    }
}

create_exception!(opsml_error, OpsmlError, PyException);
