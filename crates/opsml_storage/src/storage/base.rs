// create pyo3 async iterator
use async_trait::async_trait;
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::{FileInfo, StorageType};
use std::path::Path;
use std::path::PathBuf;
// take a stream of bytes

// create a method for Path that returns a relative path
pub struct UploadPartArgs {
    pub path: PathBuf,
}

pub trait PathExt {
    fn relative_path(&self, base: &Path) -> Result<PathBuf, StorageError>;
    fn strip_path(&self, prefix: &str) -> PathBuf;
}

impl PathExt for Path {
    fn relative_path(&self, base: &Path) -> Result<PathBuf, StorageError> {
        let result = self
            .strip_prefix(base)
            .map_err(|e| StorageError::Error(format!("Failed to get relative path: {}", e)))
            .map(|p| p.to_path_buf());

        // if result is error, check if prefix occurs in the path (this happens with LocalStorageClient) and remove anything before the prefix and the prefix itself
        if result.is_err() {
            if let Some(pos) = self.iter().position(|part| part == base) {
                let relative_path: PathBuf = self.iter().skip(pos + 1).collect();
                return Ok(relative_path);
            } else {
                return Ok(PathBuf::from(self));
            }
        }

        result
    }

    fn strip_path(&self, prefix: &str) -> PathBuf {
        self.strip_prefix(prefix).unwrap_or(self).to_path_buf()
    }
}

/// Get all files in a directory (including subdirectories)
pub fn get_files(path: &Path) -> Result<Vec<PathBuf>, StorageError> {
    let files: Vec<_> = walkdir::WalkDir::new(path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().is_file())
        .map(|e| e.path().to_path_buf())
        .collect();

    Ok(files)
}

// Define the StorageClient trait with common methods
#[async_trait]
pub trait StorageClient: Sized {
    fn storage_type(&self) -> StorageType;
    async fn bucket(&self) -> &str;
    async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError>;
    async fn find(&self, path: &str) -> Result<Vec<String>, StorageError>;
    async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError>;
    async fn get_object(&self, local_path: &str, remote_path: &str) -> Result<(), StorageError>;
    async fn copy_objects(&self, src: &str, dest: &str) -> Result<bool, StorageError>;
    async fn copy_object(&self, src: &str, dest: &str) -> Result<bool, StorageError>;
    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError>;
    async fn delete_object(&self, path: &str) -> Result<bool, StorageError>;
    async fn generate_presigned_url(
        &self,
        path: &str,
        expiration: u64,
    ) -> Result<String, StorageError>;
}

#[async_trait]
pub trait FileSystem<T: StorageClient> {
    fn name(&self) -> &str;
    fn client(&self) -> &T;

    fn storage_type(&self) -> StorageType {
        self.client().storage_type()
    }

    async fn new(settings: &OpsmlStorageSettings) -> Self;

    async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        let stripped_path = path.strip_path(self.client().bucket().await);
        self.client().find(stripped_path.to_str().unwrap()).await
    }

    async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        let stripped_path = path.strip_path(self.client().bucket().await);
        self.client()
            .find_info(stripped_path.to_str().unwrap())
            .await
    }

    async fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        // strip the paths
        let stripped_rpath = rpath.strip_path(self.client().bucket().await);
        let stripped_lpath = lpath.strip_path(self.client().bucket().await);

        if recursive {
            // list all objects in the path
            let objects = self.client().find(stripped_rpath.to_str().unwrap()).await?;

            // iterate over each object and get it
            for obj in objects {
                let file_path = Path::new(obj.as_str());
                let stripped_path = file_path.strip_path(self.client().bucket().await);
                let relative_path = file_path.relative_path(&stripped_rpath)?;
                let local_path = stripped_lpath.join(relative_path);

                self.client()
                    .get_object(
                        local_path.to_str().unwrap(),
                        stripped_path.to_str().unwrap(),
                    )
                    .await?;
            }
        } else {
            self.client()
                .get_object(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_src = src.strip_path(self.client().bucket().await);
        let stripped_dest = dest.strip_path(self.client().bucket().await);

        if recursive {
            self.client()
                .copy_objects(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        } else {
            self.client()
                .copy_object(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }
    async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_path = path.strip_path(self.client().bucket().await);

        if recursive {
            self.client()
                .delete_objects(stripped_path.to_str().unwrap())
                .await?;
        } else {
            self.client()
                .delete_object(stripped_path.to_str().unwrap())
                .await?;
        }

        Ok(())
    }
    async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        let stripped_path = path.strip_path(self.client().bucket().await);
        let objects = self.client().find(stripped_path.to_str().unwrap()).await?;

        Ok(!objects.is_empty())
    }

    async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let stripped_path = path.strip_path(self.client().bucket().await);
        self.client()
            .generate_presigned_url(stripped_path.to_str().unwrap(), expiration)
            .await
    }
}
