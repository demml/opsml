use crate::storage::http::multipart::error::MultiPartError;
use bytes::Bytes;
use opsml_client::OpsmlApiClient;
use opsml_types::contracts::{
    CompleteMultipartUpload, CompletedUploadPart, CompletedUploadParts, MultipartCompleteParts,
    UploadResponse,
};
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::Arc;

#[derive(Debug)]
pub struct S3MultipartUpload {
    upload_id: String,
    rpath: String,
    file_reader: BufReader<File>,
    completed_parts: Vec<CompletedUploadPart>,
    client: Arc<OpsmlApiClient>,
}

impl S3MultipartUpload {
    pub fn new(
        lpath: &Path,
        rpath: &Path,
        upload_id: String,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, MultiPartError> {
        let file = File::open(lpath)?;

        let file_reader = BufReader::new(file);

        Ok(Self {
            client,
            upload_id,
            rpath: rpath.to_str().unwrap().to_string(),
            file_reader,

            completed_parts: Vec::new(),
        })
    }

    pub fn upload_part(&mut self, part_number: i32, chunk: Bytes) -> Result<(), MultiPartError> {
        // First get presigned URL for this part from server
        let presigned_url = self.get_upload_url(part_number)?;

        // Upload chunk using presigned URL
        let response = self.client.client.put(&presigned_url).body(chunk).send()?;

        if response.status().is_success() {
            // Get ETag from response headers
            if let Some(e_tag) = response.headers().get("ETag") {
                self.completed_parts.push(CompletedUploadPart {
                    part_number,
                    e_tag: e_tag.to_str().unwrap().replace("\"", ""),
                });
                Ok(())
            } else {
                Err(MultiPartError::MissingEtagError)
            }
        } else {
            Err(MultiPartError::UploadError(response.status()))
        }
    }

    fn get_upload_url(&self, part_number: i32) -> Result<String, MultiPartError> {
        Ok(self.client.generate_presigned_url_for_part(
            &self.rpath,
            &self.upload_id,
            part_number,
        )?)
    }

    pub fn upload_file_in_chunks(&mut self, chunk_size: usize) -> Result<(), MultiPartError> {
        let mut buffer = vec![0; chunk_size];
        let mut part_number = 1;
        const MAX_RETRIES: u32 = 3;

        loop {
            let bytes_read = self.file_reader.read(&mut buffer)?;

            if bytes_read == 0 {
                break;
            }

            let chunk = Bytes::copy_from_slice(&buffer[..bytes_read]);

            let mut retry_count = 0;
            while retry_count < MAX_RETRIES {
                match self.upload_part(part_number, chunk.clone()) {
                    Ok(()) => break,
                    Err(e) => {
                        retry_count += 1;

                        if retry_count >= MAX_RETRIES {
                            return Err(e);
                        }

                        tracing::warn!(
                            "Retrying upload for part {} (attempt {}/{}) due to error: {}",
                            part_number,
                            retry_count,
                            MAX_RETRIES,
                            e
                        );
                    }
                }
            }

            part_number += 1;
        }

        self.complete_upload()?;

        Ok(())
    }

    fn complete_upload(&self) -> Result<UploadResponse, MultiPartError> {
        let completed_parts = CompletedUploadParts {
            parts: self.completed_parts.clone(),
        };

        let parts = MultipartCompleteParts::Aws(completed_parts);

        let request = CompleteMultipartUpload {
            path: self.rpath.clone(),
            session_url: self.upload_id.clone(),
            parts,
            cancel: false,
        };

        let response = self.client.complete_multipart_upload(request)?;

        let uploaded = response.json::<UploadResponse>()?;

        Ok(uploaded)
    }
}
