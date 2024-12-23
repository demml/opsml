use crate::storage::base::get_files;
use crate::storage::base::PathExt;
use crate::storage::http::base::{build_http_client, HttpStorageClient};
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::{FileInfo, StorageType};
use std::path::{Path, PathBuf};

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

    pub async fn new(settings: &mut OpsmlStorageSettings) -> Result<Self, StorageError> {
        let client = build_http_client(&settings.api_settings)
            .map_err(|e| StorageError::Error(format!("Failed to create http client {}", e)))?;

        Ok(HttpFSStorageClient {
            client: HttpStorageClient::new(settings, &client).await.unwrap(),
        })
    }

    pub async fn find(&mut self, path: &Path) -> Result<Vec<String>, StorageError> {
        self.client.find(path.to_str().unwrap()).await
    }

    pub async fn find_info(&mut self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        self.client.find_info(path.to_str().unwrap()).await
    }

    pub async fn get(
        &mut self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        // list all objects in the path
        let objects = self.client.find_info(rpath.to_str().unwrap()).await?;

        if recursive {
            // Iterate over each object and get it
            let mut tasks = Vec::new();

            for file_info in objects {
                let name = file_info.name;
                let file_path = PathBuf::from(name);
                let relative_path = file_path.relative_path(rpath)?;
                let local_path = lpath.join(relative_path);
                let mut cloned_client = self.client.clone();

                let task = tokio::task::spawn(async move {
                    cloned_client
                        .get_object(
                            local_path.to_str().unwrap(),
                            file_path.to_str().unwrap(),
                            file_info.size,
                        )
                        .await?;
                    Ok::<(), StorageError>(())
                });
                tasks.push(task);
            }

            // Await all tasks
            let results = futures::future::join_all(tasks).await;
            // Check for errors
            for result in results {
                result.map_err(|e| StorageError::Error(e.to_string()))??;
            }
        } else {
            let file = objects
                .first()
                .ok_or(StorageError::Error("No files found".to_string()))?;
            self.client
                .get_object(lpath.to_str().unwrap(), rpath.to_str().unwrap(), file.size)
                .await?;
        }

        Ok(())
    }

    pub async fn rm(&mut self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        if recursive {
            self.client.delete_objects(path.to_str().unwrap()).await?;
        } else {
            self.client.delete_object(path.to_str().unwrap()).await?;
        }

        Ok(())
    }

    pub async fn exists(&mut self, path: &Path) -> Result<bool, StorageError> {
        let objects = self.client.find(path.to_str().unwrap()).await?;

        Ok(!objects.is_empty())
    }

    pub async fn put(
        &mut self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        let lpath_clone = lpath.to_path_buf();
        let rpath_clone = rpath.to_path_buf();

        if recursive {
            if !lpath.is_dir() {
                return Err(StorageError::Error(
                    "Local path must be a directory for recursive put".to_string(),
                ));
            }

            let files: Vec<PathBuf> = get_files(lpath)?;

            let mut tasks = Vec::new();

            for file in files {
                let stripped_lpath_clone = lpath_clone.clone();
                let stripped_rpath_clone = rpath_clone.clone();

                let stripped_file_path = file.clone();
                let mut cloned_client = self.client.clone();

                let task = tokio::spawn(async move {
                    let relative_path = file.relative_path(&stripped_lpath_clone)?;
                    let remote_path = stripped_rpath_clone.join(relative_path);

                    let mut uploader = cloned_client
                        .create_multipart_uploader(&remote_path, &stripped_file_path)
                        .await?;

                    uploader.upload_file_in_chunks().await?;
                    Ok::<(), StorageError>(())
                });
                tasks.push(task);
            }

            let results = futures::future::join_all(tasks).await;

            for result in results {
                result.map_err(|e| StorageError::Error(e.to_string()))??;
            }

            Ok(())
        } else {
            let mut uploader = self.client.create_multipart_uploader(rpath, lpath).await?;
            uploader.upload_file_in_chunks().await?;

            Ok(())
        }
    }

    pub async fn generate_presigned_url(&mut self, path: &Path) -> Result<String, StorageError> {
        self.client
            .generate_presigned_url(path.to_str().unwrap())
            .await
    }
}
