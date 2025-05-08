use aws_sdk_s3::error::SdkError;
use aws_sdk_s3::operation::abort_multipart_upload::AbortMultipartUploadError;
use aws_sdk_s3::operation::complete_multipart_upload::CompleteMultipartUploadError;
use aws_sdk_s3::operation::copy_object::CopyObjectError;
use aws_sdk_s3::operation::create_multipart_upload::CreateMultipartUploadError;
use aws_sdk_s3::operation::delete_object::DeleteObjectError;
use aws_sdk_s3::operation::delete_objects::DeleteObjectsError;
use aws_sdk_s3::operation::get_object::GetObjectError;
use aws_sdk_s3::operation::list_objects_v2::ListObjectsV2Error;
use aws_sdk_s3::operation::upload_part::UploadPartError;
use aws_sdk_s3::presigning::PresigningConfigError;

use opsml_client::error::ApiClientError;
use reqwest::StatusCode;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AwsError {
    #[error("Invalid eTag in response: {0}")]
    InvalidEtagError(String),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    PresignError(#[from] PresigningConfigError),

    #[error(transparent)]
    CreateMultipartUploadError(#[from] SdkError<CreateMultipartUploadError>),

    #[error(transparent)]
    UploadPartError(#[from] SdkError<UploadPartError>),

    #[error(transparent)]
    CompleteUploadError(#[from] SdkError<CompleteMultipartUploadError>),

    #[error(transparent)]
    AportUploadError(#[from] SdkError<AbortMultipartUploadError>),

    #[error(transparent)]
    GetObjectError(#[from] SdkError<GetObjectError>),

    #[error(transparent)]
    ListObjectsV2Error(#[from] SdkError<ListObjectsV2Error>),

    #[error(transparent)]
    CopyObjectError(#[from] SdkError<CopyObjectError>),

    #[error(transparent)]
    DeleteObjectError(#[from] SdkError<DeleteObjectError>),

    #[error(transparent)]
    DeleteObjectsError(#[from] SdkError<DeleteObjectsError>),

    #[error("Failed to build object identifier: {0}")]
    BuildError(String),

    #[error("Failed to collect ByteStream: {0}")]
    ByteStreamError(String),

    #[error("Failed to get next chunk: {0}")]
    NextChunkError(String),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error("Invalid parts type for AWS storage")]
    InvalidPartsTypeError,

    #[error(transparent)]
    ApiClientError(#[from] ApiClientError),

    #[error("Upload failed with status: {0}")]
    UploadError(StatusCode),

    #[error("No eTag is response")]
    MissingEtagError,
}
