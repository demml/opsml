use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use opsml_types::contracts::UploadResponse;
use reqwest::multipart::{Form, Part};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::SystemTime;
use tokio::fs::File as TokioFile;
use tokio_util::io::ReaderStream;
use tracing::{debug, error, instrument};
use walkdir::WalkDir;

pub struct LocalMultipartUpload {
    lpath: String,
    rpath: String,
    client: Arc<OpsmlApiClient>,
}

impl LocalMultipartUpload {
    pub fn new(lpath: &Path, rpath: &Path, client: Arc<OpsmlApiClient>) -> Self {
        LocalMultipartUpload {
            lpath: lpath.to_str().unwrap().to_string(),
            rpath: rpath.to_str().unwrap().to_string(),
            client,
        }
    }

    pub async fn upload_file_in_chunks(
        &self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
    ) -> Result<(), StorageError> {
        let file = TokioFile::open(&self.lpath)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

        let stream = ReaderStream::new(file);

        let part = Part::stream(reqwest::Body::wrap_stream(stream))
            .file_name(self.rpath.clone())
            .mime_str("application/octet-stream")
            .map_err(|e| StorageError::Error(format!("Failed to create part: {}", e)))?;

        let form = Form::new().part("file", part);

        let response = self
            .client
            .multipart_upload(form)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to upload part: {}", e)))?;

        let response = response
            .json::<UploadResponse>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse upload response: {}", e)))?;

        if !response.uploaded {
            return Err(StorageError::Error("Failed to upload file".to_string()));
        }

        Ok(())
    }
}
