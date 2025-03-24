pub mod aws;
pub mod gcs;
pub use aws::S3MultipartUpload;
pub use gcs::GcsMultipartUpload;
use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use std::sync::Arc;

pub enum MultiPartUploader {
    S3(S3MultipartUpload),
    Gcs(GcsMultipartUpload),
}

impl MultiPartUploader {
    pub fn new(
        session_url: String,
        rpath: &str,
        lpath: &str,
        storage_type: &str,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, StorageError> {
        match storage_type {
            "s3" => {
                S3MultipartUpload::new(rpath, lpath, session_url, client).map(MultiPartUploader::S3)
            }
            "gcs" => GcsMultipartUpload::new(lpath, session_url).map(MultiPartUploader::Gcs),
            _ => Err(StorageError::Error(format!(
                "Unsupported storage type: {}",
                storage_type
            ))),
        }
    }
}
