use opsml_client::error::ApiClientError;
use opsml_settings::error::SettingsError;
use opsml_state::error::StateError;
use opsml_utils::error::UtilError;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    ApiClientError(#[from] ApiClientError),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    StateError(#[from] StateError),

    #[error(transparent)]
    SettingsError(#[from] SettingsError),

    #[error("Failed to get relative path: {0}")]
    GetRelativePathError(#[source] std::path::StripPrefixError),

    #[error(transparent)]
    SerdeQsError(#[from] serde_qs::Error),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error("Failed to parse Url: {0}")]
    ParseUrlError(String),

    #[error("No files found")]
    NoFilesFoundError,

    #[error("Local path must be a directory for recursive put")]
    PathMustBeDirectoryError,
}
