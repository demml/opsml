pub mod aws;
pub mod gcs;

pub use aws::S3MultipartUpload;
pub use gcs::GcsMultipartUpload;

pub enum MultiPartUploader {
    S3(S3MultipartUpload),
    Gcs(GcsMultipartUpload),
}

impl MultiPartUploader {
    pub fn new(session_url: String, path: &str, storage_type: &str) -> Result<Self, StorageError> {
        match storage_type {
            "s3" => S3MultipartUpload::new(session_url, path).map(MultiPartUploader::S3),
            "gcs" => GcsMultipartUpload::new(session_url, path).map(MultiPartUploader::Gcs),
            _ => Err(StorageError::Error(format!(
                "Unsupported storage type: {}",
                storage_type
            ))),
        }
    }
}
