use opsml_cards::error::CardError;
use opsml_crypt::error::CryptError;
use opsml_registry::error::RegistryError;
use opsml_storage::storage::error::StorageError;
use opsml_toml::error::PyProjectTomlError;
use opsml_types::contracts::ServiceType;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use scouter_client::ProfileError;
use std::path::PathBuf;
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

    #[error("Failed to create service card")]
    CreateServiceError(#[source] CardError),

    #[error(transparent)]
    PyProjectTomlError(#[from] PyProjectTomlError),

    #[error("Missing cards in service config")]
    MissingServiceCards,

    #[error("Card not found when loading latest")]
    MissingCardError,

    #[error("Card service is missing card entries")]
    MissingCardEntriesError,

    #[error("Failed to create write path")]
    WritePathError,

    #[error("PyProject missing tools section")]
    MissingToolsError,

    #[error("Opsml tools missing service configuration")]
    MissingServiceError,

    #[error(transparent)]
    UiError(#[from] UiError),

    #[error(transparent)]
    ManifestError(#[from] ManifestError),

    #[error(transparent)]
    ProfileError(#[from] ProfileError),

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error(transparent)]
    SkillError(#[from] opsml_cards::skill::error::SkillError),

    #[error(transparent)]
    SubAgentError(#[from] opsml_cards::subagent::SubAgentError),

    #[error(transparent)]
    ToolError(#[from] opsml_cards::ToolError),

    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    SerdeJsonError(#[from] serde_json::Error),

    #[error(transparent)]
    ServiceError(#[from] opsml_service::error::ServiceError),

    #[error("Unsupported service type: {0:?}")]
    UnsupportedServiceType(ServiceType),

    #[error("Expected a CardVariant::Card, but found a different variant")]
    ExpectedCardPathVariant,

    #[error("OpsML spec file not found at path: {0}")]
    SpecNotFound(PathBuf),
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

    #[error("Failed to get current directory")]
    CurrentDirError(#[source] std::io::Error),

    #[error("Unsupported platform - os: {0}, arch: {1}")]
    UnsupportedPlatformError(&'static str, &'static str),

    #[error("Failed to extract archive")]
    ArchiveExtractionError(#[source] std::io::Error),

    #[error("Failed to extract archive")]
    ZipArchiveExtractionError(#[source] zip::result::ZipError),

    #[error("Failed to download binary: {0}")]
    DownloadBinaryError(#[source] reqwest::Error),

    #[error("Failed to write binary: {0}")]
    WriteBinaryError(#[source] std::io::Error),

    #[error("Failed to open archive: {0}")]
    ArchiveOpenError(#[source] std::io::Error),

    #[error("Failed to unzip archive: {0}")]
    ArchiveZipError(#[source] zip::result::ZipError),

    #[error("Binary not found")]
    BinaryNotFound,

    #[error("Failed to remove archive: {0}")]
    RemoveArchiveError(#[source] std::io::Error),

    #[error("Failed to spawn child process: {0}")]
    BinarySpawnError(#[source] std::io::Error),

    #[error("Failed to wait for child process: {0}")]
    BinaryWaitError(#[source] std::io::Error),

    #[error("Failed to start the UI")]
    BinaryStartError,

    #[error("Failed to rename binary: {0}")]
    RenameBinaryError(#[source] std::io::Error),

    #[error("Failed to read file: {0}")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to remove file: {0}")]
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

    #[error("Failed to start UI server")]
    UiStartError,

    #[error("Failed to spawn UI process")]
    UiSpawnError(#[source] std::io::Error),

    #[error("Node.js executable not found. Node is required to run the OpsML UI.")]
    NodeNotFound,

    #[error("Package JSON not found")]
    PackageJsonNotFound,
}

#[derive(Error, Debug)]
pub enum ManifestError {
    #[error("Home directory not found — cannot locate manifest")]
    HomeDirNotFound,

    // Skill manifest
    #[error("Failed to read skill manifest: {0}")]
    ReadSkillManifest(#[source] std::io::Error),

    #[error("Failed to parse skill manifest: {0}")]
    ParseSkillManifest(#[source] serde_json::Error),

    #[error("Failed to create skill manifest directory: {0}")]
    CreateSkillManifestDir(#[source] std::io::Error),

    #[error("Failed to serialize skill manifest: {0}")]
    SerializeSkillManifest(#[source] serde_json::Error),

    #[error("Failed to write skill manifest: {0}")]
    WriteSkillManifest(#[source] std::io::Error),

    #[error("Failed to rename skill manifest: {0}")]
    RenameSkillManifest(#[source] std::io::Error),

    #[error("Failed to set skill manifest permissions: {0}")]
    SetSkillManifestPermissions(#[source] std::io::Error),

    // Cache manifest
    #[error("Failed to read cache manifest: {0}")]
    ReadCacheManifest(#[source] std::io::Error),

    #[error("Failed to parse cache manifest: {0}")]
    ParseCacheManifest(#[source] serde_json::Error),

    #[error("Failed to create cache manifest directory: {0}")]
    CreateCacheManifestDir(#[source] std::io::Error),

    #[error("Failed to serialize cache manifest: {0}")]
    SerializeCacheManifest(#[source] serde_json::Error),

    #[error("Failed to write cache manifest: {0}")]
    WriteCacheManifest(#[source] std::io::Error),

    #[error("Failed to rename cache manifest: {0}")]
    RenameCacheManifest(#[source] std::io::Error),

    #[error("Failed to set cache manifest permissions: {0}")]
    SetCacheManifestPermissions(#[source] std::io::Error),
}
