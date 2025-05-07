use opsml_client::error::ApiClientError;
use opsml_settings::error::SettingsError;
use opsml_state::error::StateError;
use opsml_utils::error::UtilError;
use reqwest::StatusCode;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum LocalError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Path does not exist: {0}")]
    PathNotExistError(String),
}

#[derive(Error, Debug)]
pub enum AzureError {
    #[error(transparent)]
    CoreError(#[from] azure_core::error::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error(transparent)]
    VarError(#[from] std::env::VarError),

    #[error("Invalid parts type for Azure storage")]
    InvalidPartsTypeError,
}

#[derive(Error, Debug)]
pub enum AwsError {
    #[error("No eTag is response")]
    MissingEtagError,

    #[error("Invalid eTag in response: {0}")]
    InvalidEtagError(String),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    PresignError(#[from] aws_sdk_s3::presigning::PresigningConfigError),

    #[error(transparent)]
    CreateMultipartUploadError(
        #[from]
        aws_sdk_s3::error::SdkError<
            aws_sdk_s3::operation::create_multipart_upload::CreateMultipartUploadError,
        >,
    ),

    #[error(transparent)]
    UploadPartError(
        #[from] aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::upload_part::UploadPartError>,
    ),

    #[error(transparent)]
    CompleteUploadError(
        #[from]
        aws_sdk_s3::error::SdkError<
            aws_sdk_s3::operation::complete_multipart_upload::CompleteMultipartUploadError,
        >,
    ),

    #[error(transparent)]
    AportUploadError(
        #[from]
        aws_sdk_s3::error::SdkError<
            aws_sdk_s3::operation::abort_multipart_upload::AbortMultipartUploadError,
        >,
    ),

    #[error(transparent)]
    GetObjectError(
        #[from] aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::get_object::GetObjectError>,
    ),

    #[error(transparent)]
    ListObjectsV2Error(
        #[from]
        aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::list_objects_v2::ListObjectsV2Error>,
    ),

    #[error(transparent)]
    CopyObjectError(
        #[from] aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::copy_object::CopyObjectError>,
    ),

    #[error(transparent)]
    DeleteObjectError(
        #[from]
        aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::delete_object::DeleteObjectError>,
    ),

    #[error(transparent)]
    DeleteObjectsError(
        #[from]
        aws_sdk_s3::error::SdkError<aws_sdk_s3::operation::delete_objects::DeleteObjectsError>,
    ),

    #[error("Failed to build object identifier: {0}")]
    BuildError(String),

    #[error("Failed to collect ByteStream: {0}")]
    ByteStreamError(String),

    #[error("Failed to get next chunk: {0}")]
    NextChunkError(String),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error("Upload failed with status: {0}")]
    UploadError(StatusCode),

    #[error("Invalid parts type for AWS storage")]
    InvalidPartsTypeError,

    #[error(transparent)]
    ApiClientError(#[from] ApiClientError),
}

#[derive(Error, Debug)]
pub enum GoogleError {
    #[error(transparent)]
    GCloudAuthError(#[from] google_cloud_auth::error::Error),

    #[error(transparent)]
    GCloudStorageError(#[from] google_cloud_storage::http::Error),

    #[error(transparent)]
    SignedURLError(#[from] google_cloud_storage::sign::SignedURLError),

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

#[derive(Error, Debug)]
pub enum StorageError {
    #[error(transparent)]
    AzureError(#[from] AzureError),

    #[error(transparent)]
    AwsError(#[from] AwsError),

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
    UploadFileError,

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
}
