pub mod aws;
pub mod gcs;
pub mod local;
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
                S3MultipartUpload::new(lpath, rpath, session_url, client).map(MultiPartUploader::S3)
            }
            "gcs" => GcsMultipartUpload::new(lpath, rpath, session_url, client)
                .map(MultiPartUploader::Gcs),
            _ => Err(StorageError::Error(format!(
                "Unsupported storage type: {}",
                storage_type
            ))),
        }
    }

    pub async fn upload_file_in_chunks(
        &mut self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
    ) -> Result<(), StorageError> {
        match self {
            MultiPartUploader::S3(s3) => s3.upload_file_in_chunks(chunk_size as usize).await,
            MultiPartUploader::Gcs(gcs) => {
                gcs.upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size)
                    .await
            }
        }
    }
}
