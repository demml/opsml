use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use opsml_types::contracts::UploadResponse;
use reqwest::blocking::multipart::{Form, Part};
use std::path::Path;
use std::sync::Arc;

#[derive(Debug)]
pub struct LocalMultipartUpload {
    lpath: String,
    rpath: String,
    client: Arc<OpsmlApiClient>,
}

impl LocalMultipartUpload {
    pub fn new(
        lpath: &Path,
        rpath: &Path,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, StorageError> {
        Ok(LocalMultipartUpload {
            lpath: lpath.to_str().unwrap().to_string(),
            rpath: rpath.to_str().unwrap().to_string(),
            client,
        })
    }

    pub fn upload_file_in_chunks(&self) -> Result<(), StorageError> {
        // Create multipart form with file
        let part = Part::file(&self.lpath)
            .map_err(|e| StorageError::Error(format!("Failed to create part: {}", e)))?
            .file_name(self.rpath.clone())
            .mime_str("application/octet-stream")
            .map_err(|e| StorageError::Error(format!("Failed to create part: {}", e)))?;

        let form = Form::new().part("file", part);

        let response = self
            .client
            .multipart_upload(form)
            .map_err(|e| StorageError::Error(format!("Failed to upload part: {}", e)))?;

        let response = response
            .json::<UploadResponse>()
            .map_err(|e| StorageError::Error(format!("Failed to parse upload response: {}", e)))?;

        if !response.uploaded {
            return Err(StorageError::Error("Failed to upload file".to_string()));
        }

        Ok(())
    }
}
