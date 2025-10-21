#[cfg(feature = "server")]
use crate::storage::enums::client::StorageClientEnum;

use crate::storage::error::StorageError;
use crate::storage::http::client::{AsyncHttpFSStorageClient, HttpFSStorageClient};
use async_trait::async_trait;
use opsml_settings::config::{OpsmlMode, OpsmlStorageSettings};
use opsml_state::{app_state, get_api_client, get_async_api_client};
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::FileInfo;
use opsml_types::StorageType;
use std::path::Path;
use std::sync::{Arc, RwLock};
use tokio::sync::OnceCell;
use tracing::instrument;

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

pub struct FileSystemStorage {
    #[cfg(feature = "server")]
    server: Option<StorageClientEnum>,
    client: Option<HttpFSStorageClient>,
    active_type: ActiveStorageType,
}

enum ActiveStorageType {
    #[cfg(feature = "server")]
    Server,
    Client,
}

/// FileSystemStorage implementation that is called from the client by a user (either in client or server mode)
/// when interacting with card registries. Note - this is not used in the server itself, as the server relies
/// solely on the StorageClientEnum for storage operations. Given the non-async support of Pyo3 and python's
/// non-default async support, the happy path is to enable sync only calls from the client to the server when used in
/// client mode (HttpsFSStorageClient). If the user opts to put their local code into server mode, then
/// server FileSystemStorage calls will make use of the app_state.runtime in order to interact with the StorageClientEnum.
///
impl FileSystemStorage {
    #[instrument(skip_all)]
    pub fn new() -> Result<Self, StorageError> {
        let state = app_state();
        let mode = &*state.mode()?;

        match mode {
            OpsmlMode::Server => {
                #[cfg(feature = "server")]
                {
                    let settings = state.config()?.storage_settings()?;
                    let server = Some(
                        app_state()
                            .start_runtime()
                            .block_on(async { StorageClientEnum::new(&settings).await })?,
                    );
                    Ok(Self {
                        server,
                        client: None,
                        active_type: ActiveStorageType::Server,
                    })
                }
                #[cfg(not(feature = "server"))]
                Err(StorageError::ServerFeatureError)
            }
            OpsmlMode::Client => Ok(Self {
                #[cfg(feature = "server")]
                server: None,
                client: Some(HttpFSStorageClient::new(get_api_client().clone())?),
                active_type: ActiveStorageType::Client,
            }),
        }
    }

    pub fn name(&self) -> &str {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => self.server.as_ref().unwrap().name(),
            ActiveStorageType::Client => self.client.as_ref().unwrap().name(),
        }
    }

    pub fn storage_type(&self) -> StorageType {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => self.server.as_ref().unwrap().storage_type(),
            ActiveStorageType::Client => self.client.as_ref().unwrap().storage_type(),
        }
    }

    pub fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => {
                app_state().block_on(async { self.server.as_ref().unwrap().find(path).await })
            }
            ActiveStorageType::Client => self.client.as_ref().unwrap().find(path),
        }
    }

    pub fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => {
                app_state().block_on(async { self.server.as_ref().unwrap().find_info(path).await })
            }
            ActiveStorageType::Client => self.client.as_ref().unwrap().find_info(path),
        }
    }

    pub fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => app_state().block_on(async {
                self.server
                    .as_ref()
                    .unwrap()
                    .get(lpath, rpath, recursive)
                    .await
            }),
            ActiveStorageType::Client => self.client.as_ref().unwrap().get(lpath, rpath, recursive),
        }
    }

    pub fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => app_state().block_on(async {
                self.server
                    .as_ref()
                    .unwrap()
                    .put(lpath, rpath, recursive)
                    .await
            }),
            ActiveStorageType::Client => self.client.as_ref().unwrap().put(lpath, rpath, recursive),
        }
    }

    pub fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => app_state()
                .block_on(async { self.server.as_ref().unwrap().rm(path, recursive).await }),
            ActiveStorageType::Client => self.client.as_ref().unwrap().rm(path, recursive),
        }
    }

    pub fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => {
                app_state().block_on(async { self.server.as_ref().unwrap().exists(path).await })
            }
            ActiveStorageType::Client => self.client.as_ref().unwrap().exists(path),
        }
    }

    pub async fn generate_presigned_url(
        &self,
        path: &Path,
        _expiration: u64,
    ) -> Result<String, StorageError> {
        match self.active_type {
            #[cfg(feature = "server")]
            ActiveStorageType::Server => app_state().block_on(async {
                self.server
                    .as_ref()
                    .unwrap()
                    .generate_presigned_url(path, _expiration)
                    .await
            }),
            ActiveStorageType::Client => self.client.as_ref().unwrap().generate_presigned_url(path),
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
        FileSystemStorage::new().map(Arc::new)
    }

    pub fn get_client(&self) -> Result<Arc<FileSystemStorage>, StorageError> {
        // Try to read first
        if let Ok(guard) = self.client.read() {
            if let Some(client) = guard.as_ref() {
                return Ok(client.clone());
            }
        }

        // If no client exists, create one
        let new_client = Arc::new(FileSystemStorage::new()?);

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

static ASYNC_STORAGE_CLIENT: OnceCell<Arc<AsyncHttpFSStorageClient>> = OnceCell::const_new();

// Public interface
pub fn storage_client() -> Result<Arc<FileSystemStorage>, StorageError> {
    STORAGE_MANAGER.get_client()
}

// this is only used in tests to reset state
pub fn reset_storage_client() -> Result<(), StorageError> {
    STORAGE_MANAGER.reset();
    Ok(())
}

async fn build_async_storage_client() -> Arc<AsyncHttpFSStorageClient> {
    // need to clone here so it is Send safe across threads
    let async_api_client = get_async_api_client().await.clone();

    // Initialize async API client - need an async block here
    let api_client = AsyncHttpFSStorageClient::new(async_api_client)
        .await
        .expect("Failed to create async api client");

    Arc::new(api_client)
}

pub async fn async_storage_client() -> &'static Arc<AsyncHttpFSStorageClient> {
    ASYNC_STORAGE_CLIENT
        .get_or_init(build_async_storage_client)
        .await
}

#[cfg(test)]
mod tests {
    use super::*;
    use opsml_utils::create_uuid7;
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
        let rand_name = create_uuid7();
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
        let rand_name = create_uuid7();

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
        std::env::set_var("OPSML_TRACKING_URI", "http://0.0.0.0:8080");
    }

    pub fn unset_env_vars() {
        std::env::remove_var("OPSML_TRACKING_URI");
    }

    #[test]
    fn test_gcs_storage_client() {
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
        let new_path = create_uuid7();
        let new_path = Path::new(&new_path);
        client.get(new_path, rpath, true).unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();
        client.rm(rpath, true).unwrap();

        unset_env_vars();
    }

    #[test]
    fn test_aws_storage_client() {
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
        let new_path = create_uuid7();
        let new_path = Path::new(&new_path);

        client.get(new_path, rpath, true).unwrap();

        // cleanup
        std::fs::remove_dir_all(&dirname).unwrap();
        std::fs::remove_dir_all(new_path).unwrap();

        client.rm(rpath, true).unwrap();
    }

    #[test]
    fn test_azure_storage_client() {
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
        let new_path = create_uuid7();
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

    #[test]
    fn test_local_storage_client() {
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
        let new_path = create_uuid7();
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
