use crate::storage::base::get_files;
use crate::storage::base::PathExt;
use crate::storage::http::base::HttpStorageClient;
use opsml_client::OpsmlApiClient;
use opsml_error::error::StorageError;
use opsml_state::app_state;
use opsml_types::contracts::FileInfo;
use opsml_types::StorageType;
use opsml_utils::FileUtils;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tracing::debug;
pub struct HttpFSStorageClient {
    pub client: HttpStorageClient,
}

impl HttpFSStorageClient {
    pub fn storage_type(&self) -> StorageType {
        self.client.storage_type.clone()
    }
    pub fn name(&self) -> &str {
        "HttpFSStorageClient"
    }

    pub fn new(api_client: Arc<OpsmlApiClient>) -> Result<Self, StorageError> {
        Ok(HttpFSStorageClient {
            client: HttpStorageClient::new(api_client).map_err(|e| {
                StorageError::Error(format!("Failed to create http storage client {}", e))
            })?,
        })
    }

    pub fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        self.client.find(path.to_str().unwrap())
    }

    pub fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        self.client.find_info(path.to_str().unwrap())
    }

    pub fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        // list all objects in the path
        let objects = self.client.find_info(rpath.to_str().unwrap())?;

        if recursive {
            for file_info in objects {
                let name = file_info.name;
                let file_path = PathBuf::from(name);
                let relative_path = file_path.relative_path(rpath)?;
                let local_path = lpath.join(relative_path);
                let cloned_client = self.client.clone();

                cloned_client.get_object(
                    local_path.to_str().unwrap(),
                    file_path.to_str().unwrap(),
                    file_info.size,
                )?;
            }
        } else {
            let file = objects
                .first()
                .ok_or(StorageError::Error("No files found".to_string()))?;
            self.client
                .get_object(lpath.to_str().unwrap(), rpath.to_str().unwrap(), file.size)?;
        }

        Ok(())
    }

    pub fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        if recursive {
            self.client.delete_objects(path.to_str().unwrap())?;
        } else {
            self.client.delete_object(path.to_str().unwrap())?;
        }

        Ok(())
    }

    pub fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        let objects = self.client.find(path.to_str().unwrap())?;

        Ok(!objects.is_empty())
    }

    pub fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        let lpath_clone = lpath.to_path_buf();
        let rpath_clone = rpath.to_path_buf();

        if recursive {
            if !lpath.is_dir() {
                return Err(StorageError::Error(
                    "Local path must be a directory for recursive put".to_string(),
                ));
            }

            let files: Vec<PathBuf> = get_files(lpath)?;

            for file in files {
                let (chunk_count, size_of_last_chunk, chunk_size) =
                    FileUtils::get_chunk_count(&file, 5 * 1024 * 1024)?;

                let stripped_lpath_clone = lpath_clone.clone();
                let stripped_rpath_clone = rpath_clone.clone();

                let stripped_file_path = file.clone();
                let cloned_client = self.client.clone();

                let relative_path = file.relative_path(&stripped_lpath_clone)?;
                let remote_path = stripped_rpath_clone.join(relative_path);

                debug!(
                    "remote_path: {:?}, stripped_path: {:?}",
                    remote_path, stripped_file_path
                );

                // setup multipart upload based on storage provider
                let mut uploader =
                    cloned_client.create_multipart_uploader(&remote_path, &stripped_file_path)?;

                debug!("Uploading file: {:?}", stripped_file_path);
                uploader.upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size)?;
            }
        } else {
            let (chunk_count, size_of_last_chunk, chunk_size) =
                FileUtils::get_chunk_count(&lpath_clone, 5 * 1024 * 1024)?;

            let mut uploader = self.client.create_multipart_uploader(rpath, lpath)?;
            uploader.upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size)?;
        };

        Ok(())
    }

    pub fn generate_presigned_url(&self, path: &Path) -> Result<String, StorageError> {
        self.client.generate_presigned_url(path.to_str().unwrap())
    }
}
