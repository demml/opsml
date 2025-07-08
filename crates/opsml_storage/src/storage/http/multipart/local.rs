use crate::storage::http::multipart::error::MultiPartError;
use opsml_client::OpsmlApiClient;
use opsml_types::contracts::UploadResponse;
use reqwest::blocking::multipart::{Form, Part};
use std::path::Path;
use std::sync::Arc;
use tracing::error;

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
    ) -> Result<Self, MultiPartError> {
        Ok(LocalMultipartUpload {
            lpath: lpath.to_str().unwrap().to_string(),
            rpath: rpath.to_str().unwrap().to_string(),
            client,
        })
    }

    pub fn upload_file_in_chunks(&self) -> Result<(), MultiPartError> {
        // Create multipart form with file
        let part = Part::file(&self.lpath)?
            .file_name(self.rpath.clone())
            .mime_str("application/octet-stream")?;

        let form = Form::new().part("file", part);

        let response = self.client.multipart_upload(form).map_err(|e| {
            error!("Failed to upload file: {e}");
            e
        })?;

        let response = response.json::<UploadResponse>().map_err(|e| {
            error!("Failed to parse upload response: {e}");
            e
        })?;

        if !response.uploaded {
            return Err(MultiPartError::FileUploadError);
        }

        Ok(())
    }
}
