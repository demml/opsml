use crate::storage::http::multipart::error::MultiPartError;
use indicatif::ProgressBar;
use opsml_client::OpsmlApiClient;
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
    ) -> Result<Self, MultiPartError> {
        Ok(LocalMultipartUpload {
            lpath: lpath.to_str().unwrap().to_string(),
            rpath: rpath.to_str().unwrap().to_string(),
            client,
        })
    }

    pub fn upload_file_in_chunks(&self, progress_bar: &ProgressBar) -> Result<(), MultiPartError> {
        // Create multipart form with file
        let part = Part::file(&self.lpath)?
            .file_name(self.rpath.clone())
            .mime_str("application/octet-stream")?;

        let form = Form::new().part("file", part);

        let response = self.client.multipart_upload(form)?;

        progress_bar.inc(1);

        let response = response.json::<UploadResponse>()?;

        if !response.uploaded {
            return Err(MultiPartError::FileUploadError);
        }

        progress_bar.finish_with_message("File uploaded successfully");

        Ok(())
    }
}
