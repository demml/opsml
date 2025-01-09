use crate::storage::base::get_files;
use crate::storage::base::PathExt;
use crate::storage::base::StorageClient;
use crate::storage::filesystem::FileSystem;
use async_trait::async_trait;
use futures_util::stream::Stream;
use futures_util::task::{Context, Poll};
use indicatif::{ProgressBar, ProgressStyle};
use opsml_client::OpsmlApiClient;
use opsml_colors::Colorize;
use opsml_contracts::{FileInfo, UploadResponse};
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::StorageType;
use reqwest::multipart::{Form, Part};
use std::fs::{self};
use std::path::{Path, PathBuf};
use std::pin::Pin;
use std::time::SystemTime;
use tokio::fs::File as TokioFile;
use tokio::io::AsyncRead;
use tokio_util::io::ReaderStream;
use walkdir::WalkDir;

// left off here
// removed multiupload part and implemented put on each storage client
// need to fix up http client
// - method for creating resumable upload
// - method for creating uploader from resumable upload
// - method for uploading part (special handling for local storage, or do we just use the same method?)

struct ProgressStream<R> {
    inner: ReaderStream<R>,
    progress_bar: ProgressBar,
}

impl<R: AsyncRead + Unpin> ProgressStream<R> {
    fn new(reader: R, progress_bar: ProgressBar) -> Self {
        Self {
            inner: ReaderStream::new(reader),
            progress_bar,
        }
    }
}

impl<R: AsyncRead + Unpin> Stream for ProgressStream<R> {
    type Item = Result<bytes::Bytes, std::io::Error>;

    fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        let this = self.get_mut();
        match Pin::new(&mut this.inner).poll_next(cx) {
            Poll::Ready(Some(Ok(bytes))) => {
                this.progress_bar.inc(bytes.len() as u64);
                Poll::Ready(Some(Ok(bytes)))
            }
            other => other,
        }
    }
}

pub struct LocalMultiPartUpload {
    pub lpath: PathBuf,
    pub rpath: PathBuf,
    client_mode: bool,
    api_client: Option<OpsmlApiClient>,
    pub filename: String,
}

impl LocalMultiPartUpload {
    pub async fn new(
        lpath: &str,
        rpath: &str,
        client_mode: bool,
        api_client: Option<OpsmlApiClient>,
    ) -> Result<Self, StorageError> {
        // if client_mode, api_client should be Some
        if client_mode && api_client.is_none() {
            // raise storage error
            return Err(StorageError::Error(
                "API client must be provided in client mode".to_string(),
            ));
        }

        Ok(Self {
            lpath: PathBuf::from(lpath),
            rpath: PathBuf::from(rpath),
            client_mode,
            api_client,
            filename: Path::new(lpath)
                .file_name()
                .unwrap()
                .to_string_lossy()
                .to_string(),
        })
    }

    pub async fn upload_file_in_chunks(&self) -> Result<(), StorageError> {
        // if not client mode, copy the file to rpath

        if !self.client_mode {
            // join client bucket to rpath
            // create rpath parents if they don't exist
            if let Some(parent) = self.rpath.parent() {
                fs::create_dir_all(parent).map_err(|e| {
                    StorageError::Error(format!("Failed to create directory: {}", e))
                })?;
            }

            fs::copy(&self.lpath, self.rpath.as_path())
                .map_err(|e| StorageError::Error(format!("Failed to copy file: {}", e)))?;
        } else {
            let client = self.api_client.as_ref().unwrap().clone();

            let file = TokioFile::open(&self.lpath)
                .await
                .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

            let file_size = file
                .metadata()
                .await
                .map_err(|e| StorageError::Error(format!("Failed to get file metadata: {}", e)))?
                .len();

            let bar = ProgressBar::new(file_size);
            let msg1 = Colorize::green("Uploading file:");
            let msg2 = Colorize::purple(&self.filename);
            let msg = format!("{} {}", msg1, msg2);
            let template = format!(
                "{} [{{bar:40.green/magenta}}] {{pos}}/{{len}} ({{eta}})",
                msg
            );
            let style = ProgressStyle::with_template(&template)
                .unwrap()
                .progress_chars("#--");
            bar.set_style(style);

            let stream = ProgressStream::new(file, bar.clone());

            let part = Part::stream(reqwest::Body::wrap_stream(stream))
                .file_name(self.lpath.to_str().unwrap().to_string())
                .mime_str("application/octet-stream")
                .map_err(|e| StorageError::Error(format!("Failed to create part: {}", e)))?;

            let form = Form::new().part("file", part);

            let response = client
                .multipart_upload(form)
                .await
                .map_err(|e| StorageError::Error(format!("Failed to upload part: {}", e)))?;

            bar.finish_with_message("Upload complete");

            let value = response
                .json::<serde_json::Value>()
                .await
                .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

            let response = serde_json::from_value::<UploadResponse>(value)
                .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

            if !response.uploaded {
                return Err(StorageError::Error("Failed to upload file".to_string()));
            }
        }

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
        if !bucket.exists() && !settings.client_mode {
            fs::create_dir_all(&bucket)
                .map_err(|e| {
                    StorageError::Error(format!("Unable to create bucket directory: {}", e))
                })
                .unwrap();
        }

        Ok(Self { bucket })
    }

    async fn get_object(&self, lpath: &str, rpath: &str) -> Result<(), StorageError> {
        let src_path = self.bucket.join(rpath);
        let dest_path = Path::new(lpath);

        if !src_path.exists() {
            return Err(StorageError::Error(format!(
                "Source path does not exist: {}",
                src_path.display()
            )));
        }

        if let Some(parent) = dest_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| StorageError::Error(format!("Unable to create directory: {}", e)))?;
        }

        fs::copy(&src_path, dest_path)
            .map_err(|e| StorageError::Error(format!("Unable to copy file: {}", e)))?;

        Ok(())
    }

    async fn generate_presigned_url(
        &self,
        path: &str,
        _expiration: u64,
    ) -> Result<String, StorageError> {
        let full_path = self.bucket.join(path);
        if full_path.exists() {
            Ok(full_path.to_str().unwrap().to_string())
        } else {
            Err(StorageError::Error(format!(
                "Path does not exist: {}",
                full_path.display()
            )))
        }
    }

    async fn find(&self, path: &str) -> Result<Vec<String>, StorageError> {
        let mut files = Vec::new();
        let full_path = self.bucket.join(path);
        if !full_path.exists() {
            return Ok(files);
        }

        for entry in WalkDir::new(full_path) {
            let entry = entry
                .map_err(|e| StorageError::Error(format!("Unable to read directory: {}", e)))?;
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

    async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let full_path = self.bucket.join(path);
        if !full_path.exists() {
            return Err(StorageError::Error(format!(
                "Path does not exist: {}",
                full_path.display()
            )));
        }

        let mut files_info = Vec::new();
        for entry in WalkDir::new(full_path) {
            let entry = entry
                .map_err(|e| StorageError::Error(format!("Unable to read directory: {}", e)))?;
            if entry.file_type().is_file() {
                let metadata = entry
                    .metadata()
                    .map_err(|e| StorageError::Error(format!("Unable to read metadata: {}", e)))?;
                let created = metadata
                    .created()
                    .unwrap_or(SystemTime::now())
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .unwrap()
                    .as_secs()
                    .to_string();

                let path = entry.path().to_str().unwrap().to_string();
                let path = path
                    .strip_prefix(self.bucket.to_str().unwrap())
                    .unwrap_or(&path)
                    .strip_prefix("/")
                    .unwrap_or(&path)
                    .to_string();

                let file_info = FileInfo {
                    name: path,
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
                };
                files_info.push(file_info);
            }
        }

        Ok(files_info)
    }

    async fn copy_object(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let src_path = self.bucket.join(src);
        let dest_path = self.bucket.join(dest);

        if !src_path.exists() {
            return Err(StorageError::Error(format!(
                "Source path does not exist: {}",
                src_path.display()
            )));
        }

        if let Some(parent) = dest_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| StorageError::Error(format!("Unable to create directory: {}", e)))?;
        }

        fs::copy(&src_path, &dest_path)
            .map_err(|e| StorageError::Error(format!("Unable to copy file: {}", e)))?;

        Ok(true)
    }

    async fn copy_objects(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let src_path = self.bucket.join(src);
        let dest_path = self.bucket.join(dest);

        if !src_path.exists() {
            return Err(StorageError::Error(format!(
                "Source path does not exist: {}",
                src_path.display()
            )));
        }

        for entry in WalkDir::new(&src_path) {
            let entry = entry
                .map_err(|e| StorageError::Error(format!("Unable to read directory: {}", e)))?;
            let relative_path = entry
                .path()
                .strip_prefix(&src_path)
                .map_err(|e| StorageError::Error(format!("Unable to strip prefix: {}", e)))?;
            let dest_file_path = dest_path.join(relative_path);

            if entry.file_type().is_file() {
                if let Some(parent) = dest_file_path.parent() {
                    fs::create_dir_all(parent).map_err(|e| {
                        StorageError::Error(format!("Unable to create directory: {}", e))
                    })?;
                }

                fs::copy(entry.path(), &dest_file_path)
                    .map_err(|e| StorageError::Error(format!("Unable to copy file: {}", e)))?;
            }
        }

        Ok(true)
    }

    async fn delete_object(&self, path: &str) -> Result<bool, StorageError> {
        let full_path = self.bucket.join(path);

        if !full_path.exists() {
            return Ok(true);
        }

        fs::remove_file(&full_path)
            .map_err(|e| StorageError::Error(format!("Unable to delete file: {}", e)))?;

        Ok(true)
    }

    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let full_path = self.bucket.join(path);

        if !full_path.exists() {
            return Ok(true);
        }

        for entry in WalkDir::new(&full_path) {
            let entry = entry
                .map_err(|e| StorageError::Error(format!("Unable to read directory: {}", e)))?;
            if entry.file_type().is_file() {
                fs::remove_file(entry.path())
                    .map_err(|e| StorageError::Error(format!("Unable to delete file: {}", e)))?;
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
        client_mode: bool,
        api_client: Option<OpsmlApiClient>,
    ) -> Result<LocalMultiPartUpload, StorageError> {
        // join bucket to rpath
        let rpath = self.bucket.join(rpath);
        LocalMultiPartUpload::new(lpath, rpath.to_str().unwrap(), client_mode, api_client).await
    }
}
#[derive(Clone)]
pub struct LocalFSStorageClient {
    client: LocalStorageClient,
    pub client_mode: bool,
}

#[async_trait]
impl FileSystem for LocalFSStorageClient {
    fn name(&self) -> &str {
        "LocalFSStorageClient"
    }
    async fn new(settings: &OpsmlStorageSettings) -> Self {
        let client = LocalStorageClient::new(settings).await.unwrap();
        LocalFSStorageClient {
            client,
            client_mode: settings.client_mode,
        }
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
                return Err(StorageError::Error(
                    "Local path must be a directory for recursive put".to_string(),
                ));
            }

            let files: Vec<PathBuf> = get_files(&stripped_lpath)?;

            for file in files {
                let stripped_lpath_clone = stripped_lpath.clone();
                let stripped_rpath_clone = stripped_rpath.clone();
                let stripped_file_path = file.strip_path(self.client.bucket().await);

                let relative_path = file.relative_path(&stripped_lpath_clone)?;
                let remote_path = stripped_rpath_clone.join(relative_path);

                let uploader = self
                    .create_multipart_uploader(&stripped_file_path, &remote_path, None)
                    .await?;

                uploader.upload_file_in_chunks().await?;
            }

            Ok(())
        } else {
            let uploader = self
                .create_multipart_uploader(&stripped_lpath, &stripped_rpath, None)
                .await?;

            uploader.upload_file_in_chunks().await?;
            Ok(())
        }
    }
}

impl LocalFSStorageClient {
    pub async fn create_multipart_uploader(
        &self,
        lpath: &Path,
        rpath: &Path,
        api_client: Option<OpsmlApiClient>,
    ) -> Result<LocalMultiPartUpload, StorageError> {
        self.client
            .create_multipart_uploader(
                lpath.to_str().unwrap(),
                rpath.to_str().unwrap(),
                self.client_mode,
                api_client,
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
    use opsml_error::error::StorageError;
    use opsml_settings::config::OpsmlConfig;
    use rand::distributions::Alphanumeric;
    use rand::thread_rng;
    use rand::Rng;
    use std::fs::File;
    use std::io::Write;
    use std::path::Path;
    use tempfile::TempDir;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");

        while file.metadata().unwrap().len() <= chunk_size * 2 {
            let rand_string: String = thread_rng()
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
        let rand_name = uuid::Uuid::new_v4().to_string();
        let filename = format!("file-{}.txt", rand_name);

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();

        // write file to temp dir (create_file)
        let lpath = tmp_path.join(&filename);
        create_file(lpath.to_str().unwrap(), &1024);

        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = LocalFSStorageClient::new(&settings.storage_settings()).await;

        let rpath_dir = Path::new("test_dir");
        let rpath = rpath_dir.join(&filename);

        if storage_client.exists(rpath_dir).await? {
            storage_client.rm(rpath_dir, true).await?;
        }

        assert!(!storage_client.exists(rpath_dir).await?);

        // put
        storage_client.put(&lpath, &rpath, false).await?;
        assert!(storage_client.exists(&rpath).await?);

        let nested_path = format!("nested/really/deep/file-{}.txt", rand_name);
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
        let path = current_dir.join(settings.storage_settings().storage_uri);
        std::fs::remove_dir_all(&path).unwrap();

        Ok(())
    }

    #[tokio::test]
    async fn test_local_storage_server_trees() -> Result<(), StorageError> {
        let rand_name = uuid::Uuid::new_v4().to_string();

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();
        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = LocalFSStorageClient::new(&settings.storage_settings()).await;

        let child = tmp_path.join("child");
        let grand_child = child.join("grandchild");
        for path in &[tmp_path, &child, &grand_child] {
            std::fs::create_dir_all(path).unwrap();
            let txt_file = format!("file-{}.txt", rand_name);
            let txt_path = path.join(txt_file);
            std::fs::write(&txt_path, "hello, world").unwrap();
        }

        let new_rand_name = uuid::Uuid::new_v4().to_string();
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

        let path = current_dir.join(settings.storage_settings().storage_uri);
        std::fs::remove_dir_all(&path).unwrap();

        Ok(())
    }
}
