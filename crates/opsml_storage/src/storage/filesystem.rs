#[cfg(feature = "server")]
use crate::storage::enums::client::StorageClientEnum;

use crate::storage::http::client::HttpFSStorageClient;
use async_trait::async_trait;
use opsml_error::error::StorageError;
use opsml_settings::config::{OpsmlMode, OpsmlStorageSettings};
use opsml_state::{app_state, get_api_client};
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::FileInfo;
use opsml_types::StorageType;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::{Mutex, OnceCell};
use tracing::error;
use tracing::{debug, instrument};

#[async_trait]
pub trait FileSystem {
    fn name(&self) -> &str;
    fn bucket(&self) -> &str;
    fn storage_type(&self) -> StorageType;
    async fn new(settings: &OpsmlStorageSettings) -> Self;
    async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError>;
    async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError>;
    async fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError>;
    async fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError>;
    async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError>;
    async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError>;
    async fn exists(&self, path: &Path) -> Result<bool, StorageError>;
    async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError>;

    async fn complete_multipart_upload(
        &self,
        request: CompleteMultipartUpload,
    ) -> Result<(), StorageError>;
}

pub enum FileSystemStorage {
    #[cfg(feature = "server")]
    Server(StorageClientEnum),

    Client(HttpFSStorageClient),
}

impl FileSystemStorage {
    #[instrument(skip_all)]
    pub async fn new() -> Result<Self, StorageError> {
        let state = app_state();
        let settings = state.config()?.storage_settings()?;
        let mode = state.mode()?;

        match mode {
            OpsmlMode::Server => {
                #[cfg(feature = "server")]
                {
                    debug!("Creating FileSystemStorage with StorageClientEnum for server storage");
                    return Ok(FileSystemStorage::Server(
                        StorageClientEnum::new(&settings).await?,
                    ));
                }
                #[cfg(not(feature = "server"))]
                {
                    return Err(StorageError::Error(
                        "Server mode requires the 'server' feature to be enabled".to_string(),
                    ));
                }
            }
            OpsmlMode::Client => {
                debug!("Creating FileSystemStorage with HttpFSStorageClient for client storage");

                Ok(FileSystemStorage::Client(
                    HttpFSStorageClient::new(get_api_client().await.clone()).await?,
                ))
            }
        }
    }

    pub fn name(&self) -> &str {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.name(),
            FileSystemStorage::Client(client) => client.name(),
        }
    }

    pub fn storage_type(&self) -> StorageType {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.storage_type(),
            FileSystemStorage::Client(client) => client.storage_type(),
        }
    }

    pub async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.find(path).await,
            FileSystemStorage::Client(client) => client.find(path).await,
        }
    }

    pub async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.find_info(path).await,
            FileSystemStorage::Client(client) => client.find_info(path).await,
        }
    }

    pub async fn get(
        &self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.get(lpath, rpath, recursive).await,
            FileSystemStorage::Client(client) => client.get(lpath, rpath, recursive).await,
        }
    }

    pub async fn put(
        &self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.put(lpath, rpath, recursive).await,
            FileSystemStorage::Client(client) => client.put(lpath, rpath, recursive).await,
        }
    }

    pub async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.rm(path, recursive).await,
            FileSystemStorage::Client(client) => client.rm(path, recursive).await,
        }
    }

    pub async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => client.exists(path).await,
            FileSystemStorage::Client(client) => client.exists(path).await,
        }
    }

    pub async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                client.generate_presigned_url(path, expiration).await
            }
            FileSystemStorage::Client(client) => client.generate_presigned_url(path).await,
        }
    }
}

#[derive(Default)]
pub struct StorageClientManager {
    client: OnceCell<Arc<FileSystemStorage>>,
}

impl StorageClientManager {
    pub const fn new() -> Self {
        Self {
            client: OnceCell::const_new(),
        }
    }

    pub async fn create_storage_client(&self) -> Result<Arc<FileSystemStorage>, StorageError> {
        FileSystemStorage::new().await.map(Arc::new).map_err(|e| {
            error!("Error creating FileSystemStorage: {}", e);
            StorageError::Error(format!("Error creating FileSystemStorage: {}", e))
        })
    }

    pub async fn get_client(&self) -> Arc<FileSystemStorage> {
        self.client
            .get_or_init(|| async {
                Self::create_storage_client(self)
                    .await
                    .expect("Failed to create storage client")
            })
            .await
            .clone()
    }

    pub fn reset(&mut self) {
        self.client = OnceCell::new();
    }
}

// Global static instance with interior mutability
static STORAGE_MANAGER: Mutex<StorageClientManager> = Mutex::const_new(StorageClientManager::new());

// Public interface
pub async fn storage_client() -> Arc<FileSystemStorage> {
    STORAGE_MANAGER.lock().await.get_client().await
}

// this is only used in tests to reset state
pub fn reset_storage_client() -> Result<(), StorageError> {
    app_state().start_runtime().block_on(async {
        let mut manager = STORAGE_MANAGER.lock().await;
        manager.reset();
    });

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    use rand::distr::Alphanumeric;
    use rand::rng;
    use rand::Rng;
    use std::fs::File;
    use std::io::Write;

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

    pub fn create_nested_data() -> String {
        let rand_name = uuid::Uuid::new_v4().to_string();
        let chunk_size = (1024 * 1024 * 2) as u64;

        // create a temporary directory
        let dir_name = format!("temp_test_dir_{}", &rand_name);
        let dir = Path::new(&dir_name);

        if !dir.exists() {
            std::fs::create_dir_all(dir).unwrap();
        }
        // random file name with uuid
        let key = format!("{}/temp_test_file_{}.txt", &dir_name, &rand_name);
        create_file(&key, &chunk_size);

        // created nested directories
        let dir = Path::new(&dir_name);
        let nested_dir = dir.join("nested_dir");
        let nested_dir_path = nested_dir.to_str().unwrap();

        if !nested_dir.exists() {
            std::fs::create_dir_all(nested_dir.clone()).unwrap();
        }
        // random file name with uuid
        let key = format!("{}/temp_test_file_{}.txt", &nested_dir_path, &rand_name);
        create_file(&key, &chunk_size);

        dir_name
    }

    fn _create_single_file(chunk_size: &u64) -> String {
        let rand_name = uuid::Uuid::new_v4().to_string();

        // create a temporary directory
        let dir_name = format!("temp_test_dir_{}", &rand_name);
        let dir = Path::new(&dir_name);

        if !dir.exists() {
            std::fs::create_dir_all(dir).unwrap();
        }

        // random file name with uuid
        let key = format!("{}/temp_test_file_{}.txt", &dir_name, &rand_name);
        create_file(&key, chunk_size);

        key
    }

    pub fn set_env_vars() {
        std::env::set_var("OPSML_TRACKING_URI", "http://0.0.0.0:3000");
    }

    pub fn unset_env_vars() {
        std::env::remove_var("OPSML_TRACKING_URI");
    }

    #[tokio::test]
    async fn test_gcs_storage_client() {
        set_env_vars();
        let client = FileSystemStorage::new().await.unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Google);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file

        client.put(lpath, rpath, true).await.unwrap();

        // check if the file exists
        let exists = client.exists(rpath).await.unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).await.unwrap();
        assert_eq!(files.len(), 2);

        // list files with info
        let files = client.find_info(rpath).await.unwrap();
        assert_eq!(files.len(), 2);

        // download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);
        client.get(new_path, rpath, true).await.unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();
        client.rm(rpath, true).await.unwrap();

        unset_env_vars();
    }

    #[tokio::test]
    async fn test_aws_storage_client() {
        set_env_vars();

        let client = FileSystemStorage::new().await.unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Aws);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).await.unwrap();

        // check if the file exists
        let exists = client.exists(rpath).await.unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).await.unwrap();
        assert_eq!(files.len(), 2);

        // list files with info
        let files = client.find_info(rpath).await.unwrap();
        assert_eq!(files.len(), 2);

        // download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).await.unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();

        client.rm(rpath, true).await.unwrap();
    }

    #[tokio::test]
    async fn test_azure_storage_client() {
        set_env_vars();
        let client = FileSystemStorage::new().await.unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Azure);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).await.unwrap();

        // check if the file exists
        let exists = client.exists(rpath).await.unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).await.unwrap();
        assert_eq!(files.len(), 2);

        //// list files with info
        let files = client.find_info(rpath).await.unwrap();
        assert_eq!(files.len(), 2);
        //
        //// download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).await.unwrap();

        // check if the local file exists
        let meta = std::fs::metadata(new_path).unwrap();
        assert!(meta.is_dir());
        //
        //// check number of files in the directory
        let files = std::fs::read_dir(new_path).unwrap();
        assert_eq!(files.count(), 2);
        //
        ////// cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();
        //
        client.rm(rpath, true).await.unwrap();
    }

    #[tokio::test]
    async fn test_local_storage_client() {
        set_env_vars();

        let client = FileSystemStorage::new().await.unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Local);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).await.unwrap();

        // check if the file exists
        let exists = client.exists(rpath).await.unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).await.unwrap();
        assert_eq!(files.len(), 2);
        //
        //// list files with info
        let files = client.find_info(rpath).await.unwrap();
        assert_eq!(files.len(), 2);
        //
        //// download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).await.unwrap();

        // check if the local file exists
        let meta = std::fs::metadata(new_path).unwrap();
        assert!(meta.is_dir());

        // check number of files in the directory
        let files = std::fs::read_dir(new_path).unwrap();
        assert_eq!(files.count(), 2);

        //// cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();

        client.rm(rpath, true).await.unwrap();

        // get parent of current directory

        let current_dir = std::env::current_dir().unwrap();

        // opsml_registries is 2 directories up
        let path = current_dir.join("../../opsml_registries");
        std::fs::remove_dir_all(&path).unwrap();

        unset_env_vars();
    }
}
