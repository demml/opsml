use crate::storage::base::get_files;
use crate::storage::base::PathExt;
use crate::storage::base::StorageClient;
use crate::storage::error::{LocalError, StorageError};
use crate::storage::filesystem::FileSystem;
use async_trait::async_trait;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::{contracts::FileInfo, StorageType};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::SystemTime;
use tracing::{debug, error, instrument};
use walkdir::WalkDir;

pub struct LocalMultiPartUpload {
    pub lpath: PathBuf,
    pub rpath: PathBuf,
    pub filename: String,
}

impl LocalMultiPartUpload {
    pub async fn new(lpath: &str, rpath: &str) -> Result<Self, LocalError> {
        Ok(Self {
            lpath: PathBuf::from(lpath),
            rpath: PathBuf::from(rpath),
            filename: Path::new(lpath)
                .file_name()
                .unwrap()
                .to_string_lossy()
                .to_string(),
        })
    }

    #[instrument(skip_all)]
    pub async fn upload_file_in_chunks(&self) -> Result<(), LocalError> {
        // if not client mode, copy the file to rpath

        // join client bucket to rpath
        // create rpath parents if they don't exist
        debug!("Uploading to {} via server", self.rpath.display());
        if let Some(parent) = self.rpath.parent() {
            fs::create_dir_all(parent)?;
        }

        fs::copy(&self.lpath, self.rpath.as_path())?;

        Ok(())
    }

    pub async fn complete_upload(&mut self) -> Result<(), StorageError> {
        Ok(())
    }
}
#[derive(Clone)]
pub struct LocalStorageClient {
    pub bucket: PathBuf,
}

#[async_trait]
impl StorageClient for LocalStorageClient {
    fn storage_type(&self) -> StorageType {
        StorageType::Local
    }
    async fn bucket(&self) -> &str {
        self.bucket.to_str().unwrap()
    }

    async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError> {
        let bucket = PathBuf::from(settings.storage_uri.as_str());

        // bucket should be a dir. Check if it exists. If not, create it
        if !bucket.exists() {
            fs::create_dir_all(&bucket)?;
        }

        Ok(Self { bucket })
    }

    #[instrument(skip_all)]
    async fn get_object(&self, lpath: &str, rpath: &str) -> Result<(), StorageError> {
        let src_path = self.bucket.join(rpath);
        let dest_path = Path::new(lpath);

        if !src_path.exists() {
            error!("Source path does not exist: {}", src_path.display());
            return Err(LocalError::PathNotExistError(src_path.display().to_string()).into());
        }

        if let Some(parent) = dest_path.parent() {
            fs::create_dir_all(parent)?;
        }

        fs::copy(&src_path, dest_path)?;

        Ok(())
    }

    #[instrument(skip_all)]
    async fn generate_presigned_url(
        &self,
        path: &str,
        _expiration: u64,
    ) -> Result<String, StorageError> {
        let full_path = self.bucket.join(path);
        if full_path.exists() {
            Ok(full_path.to_str().unwrap().to_string())
        } else {
            error!("Path does not exist: {}", full_path.display());
            Err(LocalError::PathNotExistError(full_path.display().to_string()).into())
        }
    }

    #[instrument(skip_all)]
    async fn find(&self, path: &str) -> Result<Vec<String>, StorageError> {
        let mut files = Vec::new();
        let full_path = self.bucket.join(path);
        if !full_path.exists() {
            return Ok(files);
        }

        for entry in WalkDir::new(full_path) {
            let entry = entry?;
            if entry.file_type().is_file() {
                files.push(entry.path().to_str().unwrap().to_string());
            }
        }

        // remove the bucket name and any following slashes
        let bucket = self.bucket.to_str().unwrap();
        let files = files
            .iter()
            .map(|f| f.strip_prefix(bucket).unwrap_or(f))
            .map(|f| f.strip_prefix("/").unwrap_or(f))
            .map(|f| f.to_string())
            .collect();

        Ok(files)
    }

    #[instrument(skip_all)]
    async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let full_path = self.bucket.join(path);
        if !full_path.exists() {
            error!("Path does not exist: {}", full_path.display());
            return Err(LocalError::PathNotExistError(full_path.display().to_string()).into());
        }

        let mut files_info = Vec::new();
        for entry in WalkDir::new(full_path) {
            let entry = entry?;
            if entry.file_type().is_file() {
                let metadata = entry.metadata()?;
                let created = metadata
                    .created()
                    .unwrap_or(SystemTime::now())
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .unwrap()
                    .as_secs()
                    .to_string();

                let rpath = entry.path().to_str().unwrap().to_string();
                let filepath = rpath
                    .strip_prefix(self.bucket.to_str().unwrap())
                    .unwrap_or(path)
                    .strip_prefix("/")
                    .unwrap_or(path)
                    .to_string();

                // strip path from rpath
                let stripped_path = filepath
                    .strip_prefix(path)
                    .unwrap_or(&rpath)
                    .strip_prefix("/")
                    .unwrap_or(&rpath)
                    .to_string();

                let file_info = FileInfo {
                    name: filepath,
                    size: metadata.len() as i64,
                    object_type: "file".to_string(),
                    created,
                    suffix: entry
                        .path()
                        .extension()
                        .unwrap_or_default()
                        .to_str()
                        .unwrap_or("")
                        .to_string(),
                    stripped_path,
                };
                files_info.push(file_info);
            }
        }

        Ok(files_info)
    }

    #[instrument(skip_all)]
    async fn copy_object(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let src_path = self.bucket.join(src);
        let dest_path = self.bucket.join(dest);

        if !src_path.exists() {
            error!("Source path does not exist: {}", src_path.display());
            return Err(LocalError::PathNotExistError(src_path.display().to_string()).into());
        }

        if let Some(parent) = dest_path.parent() {
            fs::create_dir_all(parent)?;
        }

        fs::copy(&src_path, &dest_path)?;

        Ok(true)
    }

    async fn copy_objects(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let src_path = self.bucket.join(src);
        let dest_path = self.bucket.join(dest);

        if !src_path.exists() {
            return Err(LocalError::PathNotExistError(src_path.display().to_string()).into());
        }

        for entry in WalkDir::new(&src_path) {
            let entry = entry?;
            let relative_path = entry.path().strip_prefix(&src_path)?;
            let dest_file_path = dest_path.join(relative_path);

            if entry.file_type().is_file() {
                if let Some(parent) = dest_file_path.parent() {
                    fs::create_dir_all(parent)?;
                }

                fs::copy(entry.path(), &dest_file_path)?;
            }
        }

        Ok(true)
    }

    #[instrument(skip_all)]
    async fn delete_object(&self, path: &str) -> Result<bool, StorageError> {
        let full_path = self.bucket.join(path);

        if !full_path.exists() {
            return Ok(true);
        }

        fs::remove_file(&full_path)?;

        Ok(true)
    }

    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let full_path = self.bucket.join(path);

        if !full_path.exists() {
            return Ok(true);
        }

        for entry in WalkDir::new(&full_path) {
            let entry = entry?;
            if entry.file_type().is_file() {
                fs::remove_file(entry.path())?;
            }
        }

        Ok(true)
    }
}

impl LocalStorageClient {
    pub async fn create_multipart_uploader(
        &self,
        lpath: &str,
        rpath: &str,
    ) -> Result<LocalMultiPartUpload, LocalError> {
        LocalMultiPartUpload::new(lpath, rpath).await
    }
}
#[derive(Clone)]
pub struct LocalFSStorageClient {
    client: LocalStorageClient,
}

#[async_trait]
impl FileSystem for LocalFSStorageClient {
    fn name(&self) -> &str {
        "LocalFSStorageClient"
    }
    fn bucket(&self) -> &str {
        self.client.bucket.to_str().unwrap()
    }
    async fn new(settings: &OpsmlStorageSettings) -> Self {
        let client = LocalStorageClient::new(settings).await.unwrap();
        LocalFSStorageClient { client }
    }

    fn storage_type(&self) -> StorageType {
        StorageType::Local
    }

    async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find(stripped_path.to_str().unwrap()).await
    }

    async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find_info(stripped_path.to_str().unwrap()).await
    }

    async fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        // strip the paths
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);

        if recursive {
            // list all objects in the path
            let objects = self.client.find(stripped_rpath.to_str().unwrap()).await?;

            // iterate over each object and get it
            for obj in objects {
                let file_path = Path::new(obj.as_str());
                let stripped_path = file_path.strip_path(self.client.bucket().await);
                let relative_path = file_path.relative_path(&stripped_rpath)?;
                let local_path = stripped_lpath.join(relative_path);

                self.client
                    .get_object(
                        local_path.to_str().unwrap(),
                        stripped_path.to_str().unwrap(),
                    )
                    .await?;
            }
        } else {
            self.client
                .get_object(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_src = src.strip_path(self.client.bucket().await);
        let stripped_dest = dest.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .copy_objects(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        } else {
            self.client
                .copy_object(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .delete_objects(stripped_path.to_str().unwrap())
                .await?;
        } else {
            self.client
                .delete_object(stripped_path.to_str().unwrap())
                .await?;
        }

        Ok(())
    }
    async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        let objects = self.client.find(stripped_path.to_str().unwrap()).await?;

        Ok(!objects.is_empty())
    }

    async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client
            .generate_presigned_url(stripped_path.to_str().unwrap(), expiration)
            .await
    }

    async fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);

        if recursive {
            if !stripped_lpath.is_dir() {
                return Err(StorageError::PathMustBeDirectoryError);
            }

            let files: Vec<PathBuf> = get_files(&stripped_lpath)?;
            for file in files {
                let stripped_lpath_clone = stripped_lpath.clone();
                let stripped_rpath_clone = stripped_rpath.clone();
                let stripped_file_path = file.strip_path(self.client.bucket().await);

                let relative_path = file.relative_path(&stripped_lpath_clone)?;
                let remote_path = stripped_rpath_clone.join(relative_path);

                let uploader = self
                    .create_multipart_uploader(&stripped_file_path, &remote_path)
                    .await?;

                uploader.upload_file_in_chunks().await?;
            }
        } else {
            let uploader = self
                .create_multipart_uploader(&stripped_lpath, &stripped_rpath)
                .await?;

            uploader.upload_file_in_chunks().await?;
        };

        Ok(())
    }

    async fn complete_multipart_upload(
        &self,
        _request: CompleteMultipartUpload,
    ) -> Result<(), StorageError> {
        Ok(())
    }
}

impl LocalFSStorageClient {
    pub async fn create_multipart_uploader(
        &self,
        lpath: &Path,
        rpath: &Path,
    ) -> Result<LocalMultiPartUpload, LocalError> {
        debug!(
            "Creating multipart uploader for {} -> {}",
            lpath.display(),
            rpath.display()
        );

        self.client
            .create_multipart_uploader(
                lpath.to_str().unwrap(),
                self.client.bucket.join(rpath).to_str().unwrap(),
            )
            .await
    }

    pub async fn create_multipart_upload(&self, path: &Path) -> Result<String, StorageError> {
        Ok(path.to_str().unwrap().to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::error::StorageError;
    use opsml_settings::config::OpsmlConfig;
    use opsml_utils::create_uuid7;
    use rand::distr::Alphanumeric;
    use rand::rng;
    use rand::Rng;
    use std::fs::File;
    use std::io::Write;
    use std::path::Path;
    use tempfile::TempDir;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");

        while file.metadata().unwrap().len() <= chunk_size * 2 {
            let rand_string: String = rng()
                .sample_iter(&Alphanumeric)
                .take(256)
                .map(char::from)
                .collect();
            let return_string: String = "\n".to_string();
            file.write_all(rand_string.as_ref())
                .expect("Error writing to file.");
            file.write_all(return_string.as_ref())
                .expect("Error writing to file.");
        }
    }

    #[tokio::test]
    async fn test_local_storage_server() -> Result<(), StorageError> {
        // set en vars
        let rand_name = create_uuid7();
        let filename = format!("file-{rand_name}.txt");

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();

        // write file to temp dir (create_file)
        let lpath = tmp_path.join(&filename);
        create_file(lpath.to_str().unwrap(), &1024);

        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = LocalFSStorageClient::new(&settings.storage_settings().unwrap()).await;

        let rpath_dir = Path::new("test_dir");
        let rpath = rpath_dir.join(&filename);

        if storage_client.exists(rpath_dir).await? {
            storage_client.rm(rpath_dir, true).await?;
        }

        assert!(!storage_client.exists(rpath_dir).await?);

        // put
        storage_client.put(&lpath, &rpath, false).await?;
        assert!(storage_client.exists(&rpath).await?);

        let nested_path = format!("nested/really/deep/file-{rand_name}.txt");
        let rpath_nested = rpath.parent().unwrap().join(nested_path);
        storage_client.put(&lpath, &rpath_nested, false).await?;

        let path = storage_client.generate_presigned_url(&rpath, 10).await?;
        assert!(!path.is_empty());

        // ls
        assert!(!storage_client
            .find(rpath_nested.parent().unwrap())
            .await?
            .is_empty());

        // find
        let mut blobs = storage_client.find(rpath_dir).await?;
        let mut expected_blobs = vec![
            rpath.to_str().unwrap().to_string(),
            rpath_nested.to_str().unwrap().to_string(),
        ];

        // sort the blobs
        blobs.sort();
        expected_blobs.sort();

        assert_eq!(blobs, expected_blobs,);

        // create new temp dir
        let new_tmp_dir = TempDir::new().unwrap();

        let new_lpath = new_tmp_dir.path().join(&filename);

        // get
        storage_client.get(&new_lpath, &rpath, false).await?;
        assert!(new_lpath.exists());

        // rm
        storage_client.rm(&rpath, false).await?;
        assert!(!storage_client.exists(&rpath).await?);

        // rm recursive
        storage_client.rm(rpath_dir, true).await?;
        assert!(!storage_client.exists(rpath_dir).await?);

        let current_dir = std::env::current_dir().unwrap();
        let path = current_dir.join(settings.storage_settings().unwrap().storage_uri);
        std::fs::remove_dir_all(&path).unwrap();

        Ok(())
    }

    #[tokio::test]
    async fn test_local_storage_server_trees() -> Result<(), StorageError> {
        let rand_name = create_uuid7();

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();
        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = LocalFSStorageClient::new(&settings.storage_settings().unwrap()).await;

        let child = tmp_path.join("child");
        let grand_child = child.join("grandchild");
        for path in &[tmp_path, &child, &grand_child] {
            std::fs::create_dir_all(path).unwrap();
            let txt_file = format!("file-{rand_name}.txt");
            let txt_path = path.join(txt_file);
            std::fs::write(&txt_path, "hello, world").unwrap();
        }

        let new_rand_name = create_uuid7();
        let rpath_root = Path::new(&new_rand_name);

        if storage_client.exists(rpath_root).await? {
            storage_client.rm(rpath_root, true).await?;
        }

        // put
        storage_client.put(tmp_path, rpath_root, true).await?;
        assert_eq!(storage_client.find(rpath_root).await?.len(), 3);

        // copy
        let copy_dir = rpath_root.join("copy");
        storage_client
            .copy(&rpath_root.join("child"), &copy_dir, true)
            .await?;
        assert_eq!(storage_client.find(&copy_dir).await?.len(), 2);

        // put
        let put_dir = rpath_root.join("copy2");
        storage_client.put(&child, &put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 2);

        // rm
        storage_client.rm(&put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 0);

        storage_client.rm(rpath_root, true).await?;

        let current_dir = std::env::current_dir().unwrap();

        let path = current_dir.join(settings.storage_settings().unwrap().storage_uri);
        std::fs::remove_dir_all(&path).unwrap();

        Ok(())
    }
}
