pub mod aws;
pub mod azure;
pub mod gcs;
pub mod local;
use crate::storage::error::StorageError;
pub use aws::S3MultipartUpload;
pub use azure::AzureMultipartUpload;
pub use gcs::GcsMultipartUpload;
pub use local::LocalMultipartUpload;
use opsml_client::OpsmlApiClient;
use opsml_types::StorageType;
use std::path::Path;
use std::sync::Arc;

#[derive(Debug)]
pub enum MultiPartUploader {
    S3(S3MultipartUpload),
    Gcs(GcsMultipartUpload),
    Local(LocalMultipartUpload),
    Azure(AzureMultipartUpload),
}

impl MultiPartUploader {
    pub fn new(
        rpath: &Path,
        lpath: &Path,
        storage_type: &StorageType,
        client: Arc<OpsmlApiClient>,
        session_url: String,
    ) -> Result<Self, StorageError> {
        match *storage_type {
            StorageType::Aws => Ok(S3MultipartUpload::new(lpath, rpath, session_url, client)
                .map(MultiPartUploader::S3)?),
            StorageType::Google => Ok(GcsMultipartUpload::new(lpath, rpath, session_url, client)
                .map(MultiPartUploader::Gcs)?),
            StorageType::Local => {
                LocalMultipartUpload::new(lpath, rpath, client).map(MultiPartUploader::Local)
            }
            StorageType::Azure => AzureMultipartUpload::new(lpath, rpath, session_url, client)
                .map(MultiPartUploader::Azure),
        }
    }

    pub fn upload_file_in_chunks(
        &mut self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
    ) -> Result<(), StorageError> {
        match self {
            MultiPartUploader::S3(s3) => Ok(s3.upload_file_in_chunks(chunk_size as usize)?),
            MultiPartUploader::Gcs(gcs) => {
                Ok(gcs.upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size)?)
            }
            MultiPartUploader::Local(local) => local.upload_file_in_chunks(),
            MultiPartUploader::Azure(azure) => {
                azure.upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size)
            }
        }
    }
}
