pub mod aws;
pub mod gcs;
pub use aws::S3MultipartUpload;
pub use gcs::GcsMultipartUpload;
use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use std::path::Path;
use std::sync::Arc;

pub enum MultiPartUploader {
    S3(S3MultipartUpload),
    Gcs(GcsMultipartUpload),
}

impl MultiPartUploader {
    pub fn new(
        rpath: &Path,
        lpath: &Path,
        storage_type: &str,
        client: Arc<OpsmlApiClient>,
        session_url: String,
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
