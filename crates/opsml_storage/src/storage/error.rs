use crate::storage::http::multipart::error::MultiPartError;
use opsml_client::error::ApiClientError;
use opsml_settings::error::SettingsError;
use opsml_state::error::StateError;
use opsml_utils::error::UtilError;
use thiserror::Error;

#[cfg(feature = "server")]
use crate::storage::aws::error::AwsError;
#[cfg(feature = "server")]
use crate::storage::azure::error::AzureError;
#[cfg(feature = "server")]
use crate::storage::gcs::error::GoogleError;

#[derive(Error, Debug)]
pub enum LocalError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Path does not exist: {0}")]
    PathNotExistError(String),
}

#[derive(Error, Debug)]
pub enum StorageError {
    #[cfg(feature = "server")]
    #[error(transparent)]
    AzureError(#[from] AzureError),

    #[cfg(feature = "server")]
    #[error(transparent)]
    AwsError(#[from] AwsError),

    #[cfg(feature = "server")]
    #[error(transparent)]
    GoogleError(#[from] GoogleError),

    #[error(transparent)]
    LocalError(#[from] LocalError),

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

    #[error("Failed to upload file")]
    FileUploadError,

    #[error(transparent)]
    DecodeError(#[from] base64::DecodeError),

    #[error("Failed to cancel upload")]
    CancelUploadError,

    #[error("Local and remote paths must have suffixes")]
    LocalAndRemotePathsMustHaveSuffixesError,

    #[error(transparent)]
    WalkDirError(#[from] walkdir::Error),

    #[error(transparent)]
    StripPrefixError(#[from] std::path::StripPrefixError),

    #[error("Server mode requires the 'server' feature to be enabled")]
    ServerFeatureError,

    #[error(transparent)]
    MultipartError(#[from] MultiPartError),
}
