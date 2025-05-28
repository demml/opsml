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
    CreateMultipartUploadError(#[from] Box<SdkError<CreateMultipartUploadError>>),

    #[error(transparent)]
    UploadPartError(#[from] Box<SdkError<UploadPartError>>),

    #[error(transparent)]
    CompleteUploadError(#[from] Box<SdkError<CompleteMultipartUploadError>>),

    #[error(transparent)]
    AportUploadError(#[from] Box<SdkError<AbortMultipartUploadError>>),

    #[error(transparent)]
    GetObjectError(#[from] Box<SdkError<GetObjectError>>),

    #[error(transparent)]
    ListObjectsV2Error(#[from] Box<SdkError<ListObjectsV2Error>>),

    #[error(transparent)]
    CopyObjectError(#[from] Box<SdkError<CopyObjectError>>),

    #[error(transparent)]
    DeleteObjectError(#[from] Box<SdkError<DeleteObjectError>>),

    #[error(transparent)]
    DeleteObjectsError(#[from] Box<SdkError<DeleteObjectsError>>),

    // ...existing non-SDK error variants stay the same...
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

impl From<SdkError<CreateMultipartUploadError>> for AwsError {
    fn from(err: SdkError<CreateMultipartUploadError>) -> Self {
        Self::CreateMultipartUploadError(Box::new(err))
    }
}

impl From<SdkError<UploadPartError>> for AwsError {
    fn from(err: SdkError<UploadPartError>) -> Self {
        Self::UploadPartError(Box::new(err))
    }
}

impl From<SdkError<CompleteMultipartUploadError>> for AwsError {
    fn from(err: SdkError<CompleteMultipartUploadError>) -> Self {
        Self::CompleteUploadError(Box::new(err))
    }
}

impl From<SdkError<AbortMultipartUploadError>> for AwsError {
    fn from(err: SdkError<AbortMultipartUploadError>) -> Self {
        Self::AportUploadError(Box::new(err))
    }
}
impl From<SdkError<GetObjectError>> for AwsError {
    fn from(err: SdkError<GetObjectError>) -> Self {
        Self::GetObjectError(Box::new(err))
    }
}
impl From<SdkError<ListObjectsV2Error>> for AwsError {
    fn from(err: SdkError<ListObjectsV2Error>) -> Self {
        Self::ListObjectsV2Error(Box::new(err))
    }
}
impl From<SdkError<CopyObjectError>> for AwsError {
    fn from(err: SdkError<CopyObjectError>) -> Self {
        Self::CopyObjectError(Box::new(err))
    }
}
impl From<SdkError<DeleteObjectError>> for AwsError {
    fn from(err: SdkError<DeleteObjectError>) -> Self {
        Self::DeleteObjectError(Box::new(err))
    }
}
impl From<SdkError<DeleteObjectsError>> for AwsError {
    fn from(err: SdkError<DeleteObjectsError>) -> Self {
        Self::DeleteObjectsError(Box::new(err))
    }
}
