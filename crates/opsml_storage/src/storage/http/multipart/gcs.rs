use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::UploadPartArgs;
use opsml_types::contracts::UploadResponse;
use reqwest::header::{CONTENT_LENGTH, CONTENT_RANGE};
use std::fmt;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::Arc;

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
    ) -> Result<Self, StorageError> {
        let file = File::open(lpath)
            .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

        let metadata = file
            .metadata()
            .map_err(|e| StorageError::Error(format!("Failed to get file metadata: {}", e)))?;

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

    pub async fn upload_next_chunk(
        &mut self,
        upload_args: &UploadPartArgs,
    ) -> Result<(), StorageError> {
        let first_byte = upload_args.chunk_index * upload_args.chunk_size;
        let last_byte = first_byte + upload_args.this_chunk_size - 1;

        let size = ChunkSize::new(first_byte, last_byte, Some(self.file_size));

        let mut buffer = vec![0; upload_args.this_chunk_size as usize];
        let bytes_read = self
            .file_reader
            .read(&mut buffer)
            .map_err(|e| StorageError::Error(format!("Failed to read file: {}", e)))?;

        buffer.truncate(bytes_read);

        // Upload the chunk with content-range header
        let response = self
            .client
            .client
            .put(&self.session_url)
            .header(CONTENT_RANGE, size.to_string())
            .header(CONTENT_LENGTH, size.size())
            .body(buffer)
            .send()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to upload chunk: {}", e)))?;

        if !response.status().is_success() {
            return Err(StorageError::Error(format!(
                "Failed to upload chunk: {}",
                response.status()
            )));
        }

        Ok(())
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

            // if error, cancel upload
            match self.upload_next_chunk(&upload_args).await {
                Ok(_) => (),
                Err(e) => {
                    self.cancel_upload().await?;
                    return Err(e);
                }
            }
        }

        Ok(())
    }

    //async fn complete_upload(&self) -> Result<UploadResponse, StorageError> {
    //    let request = CompleteMultipartUpload {
    //        path: self.rpath.clone(),
    //        session_url: self.session_url.clone(),
    //        ..Default::default()
    //    };
    //
    //    let response = self
    //        .client
    //        .complete_multipart_upload(request)
    //        .await
    //        .map_err(|e| StorageError::Error(format!("Failed to complete upload: {}", e)))?;
    //
    //    let uploaded = response.json::<UploadResponse>().await.map_err(|e| {
    //        StorageError::Error(format!("Failed to parse complete upload response: {}", e))
    //    })?;
    //
    //    Ok(uploaded)
    //}

    async fn cancel_upload(&self) -> Result<UploadResponse, StorageError> {
        let request = CompleteMultipartUpload {
            path: self.rpath.clone(),
            session_url: self.session_url.clone(),
            cancel: true,
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
