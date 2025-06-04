use opsml_client::error::ApiClientError;
use reqwest::Error as ReqwestError;
use reqwest::StatusCode;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MultiPartError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    ClientError(#[from] ApiClientError),

    #[error(transparent)]
    ReqwestError(#[from] ReqwestError),

    #[error("Multipart upload session creation failed: {0}")]
    CancelUploadError(String),

    #[error("Upload failed with status: {0}")]
    UploadError(StatusCode),

    #[error("No eTag is response")]
    MissingEtagError,

    #[error("Failed to upload file")]
    FileUploadError,
}
