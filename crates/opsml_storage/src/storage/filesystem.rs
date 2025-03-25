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
use std::sync::{Arc, RwLock};

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

/// FileSystemStorage implementation that is called from the client by a user (either in client or server mode)
/// when interacting with card registries. Note - this is not used in the server itself, as the server relies
/// solely on the StorageClientEnum for storage operations. Given the non-async support of Pyo3 and python's
/// non-default async support, the happy path is to enable sync only calls from the client to the server when used in
/// client mode (HttpsFSStorageClient). If the user opts to put their local code into server mode, then
/// server FileSystemStorage calls will make user of the app_state.runtime in order to interact with the StorageClientEnum.
///
impl FileSystemStorage {
    #[cfg(feature = "server")]
    fn create_server_storage(
        settings: &OpsmlStorageSettings,
    ) -> Result<FileSystemStorage, StorageError> {
        app_state().start_runtime().block_on(async {
            debug!("Creating FileSystemStorage with StorageClientEnum for server storage");
            Ok(FileSystemStorage::Server(
                StorageClientEnum::new(settings).await?,
            ))
        })
    }

    #[cfg(not(feature = "server"))]
    fn create_server_storage(
        _settings: &OpsmlStorageSettings,
    ) -> Result<FileSystemStorage, StorageError> {
        Err(StorageError::Error(
            "Server mode requires the 'server' feature to be enabled".to_string(),
        ))
    }

    #[instrument(skip_all)]
    pub fn new() -> Result<Self, StorageError> {
        let state = app_state();
        let settings = state.config()?.storage_settings()?;
        let mode = state.mode()?;

        match mode {
            OpsmlMode::Server => Self::create_server_storage(&settings),
            OpsmlMode::Client => {
                debug!("Creating FileSystemStorage with HttpFSStorageClient for client storage");

                Ok(FileSystemStorage::Client(HttpFSStorageClient::new(
                    get_api_client().clone(),
                )?))
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

    pub fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.find(path).await })
            }
            FileSystemStorage::Client(client) => client.find(path),
        }
    }

    pub fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.find_info(path).await })
            }
            FileSystemStorage::Client(client) => client.find_info(path),
        }
    }

    pub fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.get(lpath, rpath, recursive).await })
            }
            FileSystemStorage::Client(client) => client.get(lpath, rpath, recursive),
        }
    }

    pub fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.put(lpath, rpath, recursive).await })
            }
            FileSystemStorage::Client(client) => client.put(lpath, rpath, recursive),
        }
    }

    pub fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.rm(path, recursive).await })
            }
            FileSystemStorage::Client(client) => client.rm(path, recursive),
        }
    }

    pub fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => {
                app_state().block_on(async { client.exists(path).await })
            }
            FileSystemStorage::Client(client) => client.exists(path),
        }
    }

    pub async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        match self {
            #[cfg(feature = "server")]
            FileSystemStorage::Server(client) => app_state()
                .block_on(async { client.generate_presigned_url(path, expiration).await }),
            FileSystemStorage::Client(client) => client.generate_presigned_url(path),
        }
    }
}

#[derive(Default)]
pub struct StorageClientManager {
    client: RwLock<Option<Arc<FileSystemStorage>>>,
}

impl StorageClientManager {
    pub const fn new() -> Self {
        Self {
            client: RwLock::new(None),
        }
    }

    pub fn create_storage_client(&self) -> Result<Arc<FileSystemStorage>, StorageError> {
        FileSystemStorage::new().map(Arc::new).map_err(|e| {
            error!("Error creating FileSystemStorage: {}", e);
            StorageError::Error(format!("Error creating FileSystemStorage: {}", e))
        })
    }

    pub fn get_client(&self) -> Result<Arc<FileSystemStorage>, StorageError> {
        // Try to read first
        if let Ok(guard) = self.client.read() {
            if let Some(client) = guard.as_ref() {
                return Ok(client.clone());
            }
        }

        // If no client exists, create one
        let new_client = Arc::new(FileSystemStorage::new().map_err(|e| {
            error!("Error creating FileSystemStorage: {}", e);
            StorageError::Error(format!("Error creating FileSystemStorage: {}", e))
        })?);

        if let Ok(mut guard) = self.client.write() {
            if guard.is_none() {
                *guard = Some(new_client.clone());
            }
            return Ok(guard.as_ref().unwrap().clone());
        }

        // Fallback in case of poisoned lock
        Ok(new_client)
    }

    pub fn reset(&self) {
        if let Ok(mut guard) = self.client.write() {
            *guard = None;
        }
    }
}

// Global static instance
static STORAGE_MANAGER: StorageClientManager = StorageClientManager::new();

// Public interface
pub fn storage_client() -> Result<Arc<FileSystemStorage>, StorageError> {
    STORAGE_MANAGER.get_client()
}

// this is only used in tests to reset state
pub fn reset_storage_client() -> Result<(), StorageError> {
    STORAGE_MANAGER.reset();
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
        let client = FileSystemStorage::new().unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Google);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file

        client.put(lpath, rpath, true).unwrap();

        // check if the file exists
        let exists = client.exists(rpath).unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).unwrap();
        assert_eq!(files.len(), 2);

        // list files with info
        let files = client.find_info(rpath).unwrap();
        assert_eq!(files.len(), 2);

        // download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);
        client.get(new_path, rpath, true).unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();
        client.rm(rpath, true).unwrap();

        unset_env_vars();
    }

    #[tokio::test]
    async fn test_aws_storage_client() {
        set_env_vars();

        let client = FileSystemStorage::new().unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Aws);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).unwrap();

        // check if the file exists
        let exists = client.exists(rpath).unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).unwrap();
        assert_eq!(files.len(), 2);

        // list files with info
        let files = client.find_info(rpath).unwrap();
        assert_eq!(files.len(), 2);

        // download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();

        client.rm(rpath, true).unwrap();
    }

    #[tokio::test]
    async fn test_azure_storage_client() {
        set_env_vars();
        let client = FileSystemStorage::new().unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Azure);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).unwrap();

        // check if the file exists
        let exists = client.exists(rpath).unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).unwrap();
        assert_eq!(files.len(), 2);

        //// list files with info
        let files = client.find_info(rpath).unwrap();
        assert_eq!(files.len(), 2);
        //
        //// download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).unwrap();

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
        client.rm(rpath, true).unwrap();
    }

    #[tokio::test]
    async fn test_local_storage_client() {
        set_env_vars();

        let client = FileSystemStorage::new().unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::Local);

        let dirname = create_nested_data();

        let lpath = Path::new(&dirname);
        let rpath = Path::new(&dirname);

        // put the file
        client.put(lpath, rpath, true).unwrap();

        // check if the file exists
        let exists = client.exists(rpath).unwrap();
        assert!(exists);

        // list all files
        let files = client.find(rpath).unwrap();
        assert_eq!(files.len(), 2);
        //
        //// list files with info
        let files = client.find_info(rpath).unwrap();
        assert_eq!(files.len(), 2);
        //
        //// download the files
        let new_path = uuid::Uuid::new_v4().to_string();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).unwrap();

        // check if the local file exists
        let meta = std::fs::metadata(new_path).unwrap();
        assert!(meta.is_dir());

        // check number of files in the directory
        let files = std::fs::read_dir(new_path).unwrap();
        assert_eq!(files.count(), 2);

        //// cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();

        client.rm(rpath, true).unwrap();

        // get parent of current directory

        let current_dir = std::env::current_dir().unwrap();

        // opsml_registries is 2 directories up
        let path = current_dir.join("../../opsml_registries");
        std::fs::remove_dir_all(&path).unwrap();

        unset_env_vars();
    }
}
