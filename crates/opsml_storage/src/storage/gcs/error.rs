use google_cloud_auth::error::Error as GCloudAuthError;
use google_cloud_storage::http::Error as GCloudStorageError;
use google_cloud_storage::sign::SignedURLError;

use opsml_client::error::ApiClientError;

use reqwest::StatusCode;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum GoogleError {
    #[error(transparent)]
    GCloudAuthError(#[from] GCloudAuthError),

    #[error(transparent)]
    GCloudStorageError(#[from] GCloudStorageError),

    #[error(transparent)]
    SignedURLError(#[from] SignedURLError),

    #[error(transparent)]
    DecodeError(#[from] base64::DecodeError),

    #[error(transparent)]
    Utf8Error(#[from] std::string::FromUtf8Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Failed to upload chunks")]
    UploadChunksError,

    #[error("Upload failed with status: {0}")]
    UploadError(StatusCode),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error(transparent)]
    ApiClientError(#[from] ApiClientError),
}
