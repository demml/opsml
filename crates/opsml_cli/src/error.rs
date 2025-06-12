use opsml_cards::error::CardError;
use opsml_crypt::error::CryptError;
use opsml_registry::error::RegistryError;
use opsml_storage::storage::error::StorageError;
use opsml_toml::error::PyProjectTomlError;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use scouter_client::ProfileError;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum CliError {
    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error("Failed to load card deck JSON file")]
    LoadCardDeckError(#[source] CardError),

    #[error("Failed to create card deck")]
    CreateDeckError(#[source] CardError),

    #[error(transparent)]
    PyProjectTomlError(#[from] PyProjectTomlError),

    #[error("Missing cards in deck config")]
    MissingDeckCards,

    #[error("Card not found when loading latest")]
    MissingCardError,

    #[error("Card deck is missing card entries")]
    MissingCardEntriesError,

    #[error("Failed to create write path")]
    WritePathError,

    #[error("PyProject missing tools section")]
    MissingToolsError,

    #[error("Opsml tools missing app configuration")]
    MissingAppError,

    #[error(transparent)]
    UiError(#[from] UiError),

    #[error(transparent)]
    ProfileError(#[from] ProfileError),

    #[error(transparent)]
    CardError(#[from] CardError),
}

impl From<CliError> for PyErr {
    fn from(err: CliError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum UiError {
    #[error("Failed to get home directory")]
    HomeDirError,

    #[error("Failed to get create cache directory")]
    CreateCacheDirError(#[source] std::io::Error),

    #[error("Unsupported platform - os: {0}, arch: {1}")]
    UnsupportedPlatformError(&'static str, &'static str),

    #[error("Failed to extract archive")]
    ArchiveExtractionError(#[source] std::io::Error),

    #[error("Failed to extract archive")]
    ZipArchiveExtractionError(#[source] zip::result::ZipError),

    #[error("Failed to download binary")]
    DownloadBinaryError(#[source] reqwest::Error),

    #[error("Failed to write binary")]
    WriteBinaryError(#[source] std::io::Error),

    #[error("Failed to open archive")]
    ArchiveOpenError(#[source] std::io::Error),

    #[error("Failed to unzip archive")]
    ArchiveZipError(#[source] zip::result::ZipError),

    #[error("Binary not found")]
    BinaryNotFound,

    #[error("Failed to remove archive")]
    RemoveArchiveError(#[source] std::io::Error),

    #[error("Failed to spawn child process")]
    BinarySpawnError(#[source] std::io::Error),

    #[error("Failed to wait for child process")]
    BinaryWaitError(#[source] std::io::Error),

    #[error("Failed to start the UI")]
    BinaryStartError,

    #[error("Failed to rename binary")]
    RenameBinaryError(#[source] std::io::Error),

    #[error("Failed to read file")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to remove file")]
    RemoveFileError(#[source] std::io::Error),

    #[error("Could not extract UI archive due to unsupported platform")]
    UnsupportedPlatformExtractionError,

    #[error("No running OpsML server found")]
    NoRunningServer,

    #[error("Failed to read process ID from file")]
    ProcessIdReadError(#[source] std::io::Error),

    #[error("Failed to parse process ID from file")]
    ProcessIdParseError(#[source] std::num::ParseIntError),

    #[error("Failed to write process ID to file")]
    ProcessIdWriteError(#[source] std::io::Error),

    #[error("Failed to kill process: {0}")]
    ProcessKillError(String),

    #[error("Python executable not found")]
    PythonNotFound,

    #[error("Failed to execute script")]
    ScriptExecutionError,

    #[error("Script execution failed with status code: {0:?}")]
    ScriptFailedWithStatus(Option<i32>),
}
