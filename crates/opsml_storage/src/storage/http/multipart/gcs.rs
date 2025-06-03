use crate::storage::http::multipart::error::MultiPartError;
use opsml_client::OpsmlApiClient;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::UploadPartArgs;
use opsml_types::contracts::UploadResponse;
use reqwest::header::{CONTENT_LENGTH, CONTENT_RANGE};
use std::fmt;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::Arc;
use tracing::error;
use tracing::instrument;

#[derive(Clone, Debug)]
pub struct ChunkSize {
    first_byte: u64,
    last_byte: u64,
    total_object_size: Option<u64>,
}

impl ChunkSize {
    pub fn new(first_byte: u64, last_byte: u64, total_object_size: Option<u64>) -> ChunkSize {
        Self {
            first_byte,
            last_byte,
            total_object_size,
        }
    }

    pub fn size(&self) -> u64 {
        match self.total_object_size {
            Some(size) if size == self.first_byte => 0,
            _ => self.last_byte - self.first_byte + 1,
        }
    }
}

impl fmt::Display for ChunkSize {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // First part: handle the byte range
        match (self.total_object_size, self.first_byte) {
            (Some(size), first) if size == first => write!(f, "bytes */")?,
            _ => write!(f, "bytes {}-{}/", self.first_byte, self.last_byte)?,
        };

        // Second part: handle the total size
        match self.total_object_size {
            Some(size) => write!(f, "{size}"),
            None => write!(f, "*"),
        }
    }
}

#[derive(Debug)]
pub struct GcsMultipartUpload {
    session_url: String,
    file_reader: BufReader<File>,
    file_size: u64,
    rpath: String,
    client: Arc<OpsmlApiClient>,
}

impl GcsMultipartUpload {
    pub fn new(
        lpath: &Path,
        rpath: &Path,
        session_url: String,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, MultiPartError> {
        let file = File::open(lpath)?;

        let metadata = file.metadata()?;

        let file_size = metadata.len();
        let file_reader = BufReader::new(file);

        Ok(GcsMultipartUpload {
            client,
            session_url,
            file_reader,
            file_size,
            rpath: rpath.to_str().unwrap().to_string(),
        })
    }

    pub fn upload_next_chunk(
        &mut self,
        upload_args: &UploadPartArgs,
    ) -> Result<bool, MultiPartError> {
        let first_byte = upload_args.chunk_index * upload_args.chunk_size;
        let last_byte = first_byte + upload_args.this_chunk_size - 1;

        let size = ChunkSize::new(first_byte, last_byte, Some(self.file_size));

        // trace the size of the chunk being uploaded in mbs
        tracing::trace!(
            "Uploading chunk {} with  bytes ({} MB)",
            upload_args.chunk_index,
            size.size() as f64 / (1024.0 * 1024.0)
        );

        let mut buffer = vec![0; upload_args.this_chunk_size as usize];
        let bytes_read = self.file_reader.read(&mut buffer)?;

        buffer.truncate(bytes_read);

        // Upload the chunk with content-range header
        let response = self
            .client
            .client
            .put(&self.session_url)
            .header(CONTENT_RANGE, size.to_string())
            .header(CONTENT_LENGTH, size.size())
            .body(buffer)
            .send()?;

        if response.status() == reqwest::StatusCode::PERMANENT_REDIRECT {
            tracing::debug!(
                "Chunk {} uploaded successfully (308 Resume Incomplete)",
                upload_args.chunk_index
            );
            return Ok(false); // Not finished yet
        } else if response.status().is_success() {
            tracing::debug!(
                "Upload completed successfully with status: {}",
                response.status()
            );
            return Ok(true); // Upload complete
        } else {
            return Err(MultiPartError::UploadError(response.status()));
        }
    }

    #[instrument(skip_all)]
    pub fn upload_file_in_chunks(
        &mut self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
    ) -> Result<(), MultiPartError> {
        let mut upload_complete = false;
        for chunk_index in 0..chunk_count {
            let this_chunk = if chunk_count - 1 == chunk_index {
                size_of_last_chunk
            } else {
                chunk_size
            };

            let upload_args = UploadPartArgs {
                chunk_size,
                chunk_index,
                this_chunk_size: this_chunk,
            };

            const MAX_RETRIES: u32 = 3;
            let mut retry_count = 0;

            while retry_count < MAX_RETRIES {
                match self.upload_next_chunk(&upload_args) {
                    Ok(is_complete) => {
                        upload_complete = is_complete;
                        // If we got a 308, this is normal for chunked uploads
                        break;
                    }
                    Err(e) => {
                        retry_count += 1;
                        if retry_count == MAX_RETRIES {
                            error!(
                                "Error uploading chunk {} after {} retries: {}",
                                chunk_index, MAX_RETRIES, e
                            );
                            if let Err(cancel_err) = self.cancel_upload() {
                                error!("Failed to cancel upload after error: {}", cancel_err);
                            }
                            return Err(e);
                        }

                        tracing::warn!("Retry {} for chunk {}: {}", retry_count, chunk_index, e);
                        std::thread::sleep(std::time::Duration::from_millis(
                            500 * retry_count as u64,
                        ));
                    }
                }
            }

            // If the upload was marked complete before the last chunk, we can exit early
            if upload_complete && chunk_index < chunk_count - 1 {
                tracing::info!(
                    "Upload completed early at chunk {}/{}",
                    chunk_index + 1,
                    chunk_count
                );
                break;
            }
        }

        if !upload_complete {
            tracing::warn!("Upload may be incomplete - never received final success status");
        }

        Ok(())
    }

    fn cancel_upload(&self) -> Result<UploadResponse, MultiPartError> {
        let request = CompleteMultipartUpload {
            path: self.rpath.clone(),
            session_url: self.session_url.clone(),
            cancel: true,
            ..Default::default()
        };

        let response = self.client.complete_multipart_upload(request)?;
        let uploaded = response.json::<UploadResponse>()?;

        Ok(uploaded)
    }
}
