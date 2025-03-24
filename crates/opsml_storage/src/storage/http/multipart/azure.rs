use base64::prelude::*;
use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::MultipartCompleteParts;
use opsml_types::contracts::UploadPartArgs;
use opsml_types::contracts::UploadResponse;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::Arc;

#[derive(Debug)]
pub struct AzureMultipartUpload {
    session_url: String,
    file_reader: BufReader<File>,
    client: Arc<OpsmlApiClient>,
    block_parts: Vec<String>,
    rpath: String,
}

impl AzureMultipartUpload {
    pub fn new(
        lpath: &Path,
        rpath: &Path,
        session_url: String,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, StorageError> {
        let file = File::open(lpath)
            .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

        let file_reader = BufReader::new(file);

        Ok(Self {
            client,
            session_url: session_url.to_string(),
            block_parts: Vec::new(),
            file_reader,
            rpath: rpath.to_str().unwrap().to_string(),
        })
    }

    pub async fn upload_file_in_chunks(
        &mut self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
    ) -> Result<(), StorageError> {
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

            self.upload_next_chunk(&upload_args).await?;
        }

        self.complete_upload().await?;

        Ok(())
    }

    pub async fn upload_block(&self, block_id: &str, data: &[u8]) -> Result<(), StorageError> {
        let url = format!(
            "{}&comp=block&blockid={}",
            self.session_url,
            BASE64_STANDARD.encode(block_id)
        );

        self.client
            .client
            .put(&url)
            .body(data.to_vec())
            .send()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to upload block: {:?}", e)))?;

        Ok(())
    }

    pub async fn upload_next_chunk(
        &mut self,
        upload_args: &UploadPartArgs,
    ) -> Result<(), StorageError> {
        let mut buffer = vec![0; upload_args.this_chunk_size as usize];
        let bytes_read = self
            .file_reader
            .read(&mut buffer)
            .map_err(|e| StorageError::Error(format!("Failed to read file: {}", e)))?;

        buffer.truncate(bytes_read);

        let block_id = format!("{:06}", upload_args.chunk_index);

        self.upload_block(&block_id, &buffer).await.map_err(|e| {
            StorageError::Error(format!(
                "Unable to upload multiple chunks to resumable upload: {}",
                e
            ))
        })?;

        self.block_parts.push(block_id);

        Ok(())
    }

    pub async fn complete_upload(&self) -> Result<UploadResponse, StorageError> {
        let parts = MultipartCompleteParts::Azure(self.block_parts.clone());
        let request = CompleteMultipartUpload {
            path: self.rpath.clone(),
            session_url: self.session_url.clone(),
            parts,
            ..Default::default()
        };

        let response = self
            .client
            .complete_multipart_upload(request)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to complete upload: {}", e)))?;

        let uploaded = response.json::<UploadResponse>().await.map_err(|e| {
            StorageError::Error(format!("Failed to parse complete upload response: {}", e))
        })?;

        Ok(uploaded)
    }
}
