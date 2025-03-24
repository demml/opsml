use bytes::Bytes;
use opsml_client::OpsmlApiClient;
use opsml_error::StorageError;
use reqwest::Client;
use serde::Serialize;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::Arc;

pub struct S3MultipartUpload {
    upload_id: String,
    bucket: String,
    key: String,
    file_reader: BufReader<File>,
    file_size: u64,
    completed_parts: Vec<CompletedPart>,
    api_url: String,
    client: Arc<OpsmlApiClient>,
}

#[derive(Debug, Serialize)]
struct CompletedPart {
    PartNumber: i32,
    ETag: String,
}

impl S3MultipartUpload {
    pub fn new(
        api_url: String,
        bucket: String,
        key: String,
        upload_id: String,
        path: &str,
        client: Arc<OpsmlApiClient>,
    ) -> Result<Self, StorageError> {
        let file = File::open(path)
            .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

        let file_size = file
            .metadata()
            .map_err(|e| StorageError::Error(format!("Failed to get file metadata: {}", e)))?
            .len();

        let file_reader = BufReader::new(file);

        Ok(Self {
            client,
            upload_id,
            bucket,
            key,
            file_reader,
            file_size,
            completed_parts: Vec::new(),
            api_url,
        })
    }

    pub async fn upload_part(
        &mut self,
        part_number: i32,
        chunk: Bytes,
    ) -> Result<(), StorageError> {
        // First get presigned URL for this part from server
        let presigned_url = self.get_upload_url(part_number).await?;

        // Upload chunk using presigned URL
        let response = self
            .client
            .client
            .put(&presigned_url)
            .body(chunk)
            .send()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to upload part: {}", e)))?;

        if response.status().is_success() {
            // Get ETag from response headers
            if let Some(etag) = response.headers().get("ETag") {
                self.completed_parts.push(CompletedPart {
                    PartNumber: part_number,
                    ETag: etag.to_str().unwrap().replace("\"", ""),
                });
                Ok(())
            } else {
                Err(StorageError::Error("No ETag in response".to_string()))
            }
        } else {
            Err(StorageError::Error(format!(
                "Upload failed with status: {}",
                response.status()
            )))
        }
    }

    async fn get_upload_url(&self, part_number: i32) -> Result<String, StorageError> {
        self.client
            .generate_presigned_url_for_part(&self.key, &self.upload_id, part_number)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to get presigned URL: {}", e)))
    }

    pub async fn upload_file_in_chunks(&mut self, chunk_size: usize) -> Result<(), StorageError> {
        let mut buffer = vec![0; chunk_size];
        let mut part_number = 1;

        loop {
            let bytes_read = self
                .file_reader
                .read(&mut buffer)
                .map_err(|e| StorageError::Error(format!("Failed to read file: {}", e)))?;

            if bytes_read == 0 {
                break;
            }

            let chunk = Bytes::copy_from_slice(&buffer[..bytes_read]);
            self.upload_part(part_number, chunk).await?;

            part_number += 1;
        }

        self.complete_upload().await
    }

    async fn complete_upload(&self) -> Result<(), StorageError> {
        let response = self
            .client
            .post(&format!(
                "{}/complete-upload?bucket={}&key={}&uploadId={}",
                self.api_url, self.bucket, self.key, self.upload_id
            ))
            .json(&self.completed_parts)
            .send()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to complete upload: {}", e)))?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(StorageError::Error("Failed to complete upload".to_string()))
        }
    }
}

// Usage example:
pub async fn upload_file(
    api_url: &str,
    bucket: &str,
    key: &str,
    local_path: &str,
) -> Result<(), StorageError> {
    // First request upload ID from server
    let client = Client::new();
    let response = client
        .post(&format!(
            "{}/start-upload?bucket={}&key={}",
            api_url, bucket, key
        ))
        .send()
        .await?;

    let upload_id = response.text().await?;

    // Create uploader
    let mut uploader = S3MultipartUpload::new(
        api_url.to_string(),
        bucket.to_string(),
        key.to_string(),
        upload_id,
        local_path,
    )?;

    // Upload file in chunks
    uploader.upload_file_in_chunks(5 * 1024 * 1024).await // 5MB chunks
}
