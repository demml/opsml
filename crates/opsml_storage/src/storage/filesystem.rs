use crate::storage::enums::client::StorageClientEnum;
use crate::storage::http::client::HttpFSStorageClient;
use async_trait::async_trait;
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::{FileInfo, StorageType};
use std::path::Path;

#[async_trait]
pub trait FileSystem {
    fn name(&self) -> &str;
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
}

pub struct FileSystemStorage {
    fs: Option<StorageClientEnum>,
    http: Option<HttpFSStorageClient>,
    client_mode: bool,
}

impl FileSystemStorage {
    pub async fn new(settings: &mut OpsmlStorageSettings) -> Result<Self, StorageError> {
        if !settings.client_mode {
            Ok(FileSystemStorage {
                fs: Some(StorageClientEnum::new(settings).await?),
                http: None,
                client_mode: settings.client_mode,
            })
        } else {
            Ok(FileSystemStorage {
                fs: None,
                http: Some(HttpFSStorageClient::new(&mut *settings).await?),
                client_mode: settings.client_mode,
            })
        }
    }

    pub fn name(&self) -> &str {
        if self.client_mode {
            self.http.as_ref().unwrap().name()
        } else {
            self.fs.as_ref().unwrap().name()
        }
    }

    pub fn storage_type(&self) -> StorageType {
        if self.client_mode {
            self.http.as_ref().unwrap().storage_type()
        } else {
            self.fs.as_ref().unwrap().storage_type()
        }
    }

    pub async fn find(&mut self, path: &Path) -> Result<Vec<String>, StorageError> {
        if self.client_mode {
            self.http.as_mut().unwrap().find(path).await
        } else {
            self.fs.as_ref().unwrap().find(path).await
        }
    }

    pub async fn find_info(&mut self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        if self.client_mode {
            self.http.as_mut().unwrap().find_info(path).await
        } else {
            self.fs.as_ref().unwrap().find_info(path).await
        }
    }

    pub async fn get(
        &mut self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        if self.client_mode {
            self.http
                .as_mut()
                .unwrap()
                .get(lpath, rpath, recursive)
                .await
        } else {
            self.fs.as_ref().unwrap().get(lpath, rpath, recursive).await
        }
    }

    pub async fn put(
        &mut self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        if self.client_mode {
            self.http
                .as_mut()
                .unwrap()
                .put(lpath, rpath, recursive)
                .await
        } else {
            self.fs.as_ref().unwrap().put(lpath, rpath, recursive).await
        }
    }

    pub async fn rm(&mut self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        if self.client_mode {
            self.http.as_mut().unwrap().rm(path, recursive).await
        } else {
            self.fs.as_ref().unwrap().rm(path, recursive).await
        }
    }

    pub async fn exists(&mut self, path: &Path) -> Result<bool, StorageError> {
        if self.client_mode {
            self.http.as_mut().unwrap().exists(path).await
        } else {
            self.fs.as_ref().unwrap().exists(path).await
        }
    }

    pub async fn generate_presigned_url(
        &mut self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        if self.client_mode {
            self.http
                .as_mut()
                .unwrap()
                .generate_presigned_url(path)
                .await
        } else {
            self.fs
                .as_ref()
                .unwrap()
                .generate_presigned_url(path, expiration)
                .await
        }
    }
}

//#[pyclass]
//pub struct PyFileSystemStorage {
//    fs: Option<StorageClientEnum>,
//    http: Option<HttpFSStorageClient>,
//    client_mode: bool,
//    runtime: tokio::runtime::Runtime,
//}
//
//#[pymethods]
//impl PyFileSystemStorage {
//    #[new]
//    pub fn new(settings: &mut OpsmlStorageSettings) -> PyResult<Self> {
//        let rt = tokio::runtime::Runtime::new().unwrap();
//
//        let (fs, http) = rt
//            .block_on(async {
//                let fs = if !settings.client_mode {
//                    Some(StorageClientEnum::new(settings).await?)
//                } else {
//                    None
//                };
//
//                let http = if settings.client_mode {
//                    Some(HttpFSStorageClient::new(&mut *settings).await?)
//                } else {
//                    None
//                };
//
//                Ok::<(Option<StorageClientEnum>, Option<HttpFSStorageClient>), StorageError>((
//                    fs, http,
//                ))
//            })
//            .unwrap();
//
//        Ok(PyFileSystemStorage {
//            fs,
//            http,
//            client_mode: settings.client_mode,
//            runtime: rt,
//        })
//    }
//
//    pub fn name(&self) -> &str {
//        if self.client_mode {
//            self.http.as_ref().unwrap().name()
//        } else {
//            self.fs.as_ref().unwrap().name()
//        }
//    }
//
//    pub fn storage_type(&self) -> StorageType {
//        if self.client_mode {
//            self.http.as_ref().unwrap().storage_type()
//        } else {
//            self.fs.as_ref().unwrap().storage_type()
//        }
//    }
//
//    #[pyo3(signature = (path=PathBuf::new()))]
//    pub fn find(&mut self, path: PathBuf) -> PyResult<Vec<String>> {
//        Ok(self
//            .runtime
//            .block_on(async {
//                if self.client_mode {
//                    self.http.as_mut().unwrap().find(&path).await
//                } else {
//                    self.fs.as_ref().unwrap().find(&path).await
//                }
//            })
//            .unwrap())
//    }
//
//    #[pyo3(signature = (path=PathBuf::new()))]
//    pub fn find_info(&mut self, path: PathBuf) -> PyResult<Vec<FileInfo>> {
//        Ok(self
//            .runtime
//            .block_on(async {
//                if self.client_mode {
//                    self.http.as_mut().unwrap().find_info(&path).await
//                } else {
//                    self.fs.as_ref().unwrap().find_info(&path).await
//                }
//            })
//            .unwrap())
//    }
//
//    #[pyo3(signature = (lpath, rpath, recursive = false))]
//    pub fn get(&mut self, lpath: PathBuf, rpath: PathBuf, recursive: bool) -> PyResult<()> {
//        self.runtime.block_on(async {
//            if self.client_mode {
//                self.http
//                    .as_mut()
//                    .unwrap()
//                    .get(&lpath, &rpath, recursive)
//                    .await
//            } else {
//                self.fs
//                    .as_ref()
//                    .unwrap()
//                    .get(&lpath, &rpath, recursive)
//                    .await
//            }
//        })?;
//        Ok(())
//    }
//
//    #[pyo3(signature = (lpath, rpath, recursive = false))]
//    pub fn put(&mut self, lpath: PathBuf, rpath: PathBuf, recursive: bool) -> PyResult<()> {
//        self.runtime.block_on(async {
//            if self.client_mode {
//                self.http
//                    .as_mut()
//                    .unwrap()
//                    .put(&lpath, &rpath, recursive)
//                    .await
//            } else {
//                self.fs
//                    .as_ref()
//                    .unwrap()
//                    .put(&lpath, &rpath, recursive)
//                    .await
//            }
//        })?;
//        Ok(())
//    }
//
//    #[pyo3(signature = (path, recursive = false))]
//    pub fn rm(&mut self, path: PathBuf, recursive: bool) -> PyResult<()> {
//        self.runtime.block_on(async {
//            if self.client_mode {
//                self.http.as_mut().unwrap().rm(&path, recursive).await
//            } else {
//                self.fs.as_ref().unwrap().rm(&path, recursive).await
//            }
//        })?;
//        Ok(())
//    }
//
//    pub fn exists(&mut self, path: PathBuf) -> PyResult<bool> {
//        Ok(self
//            .runtime
//            .block_on(async {
//                if self.client_mode {
//                    self.http.as_mut().unwrap().exists(&path).await
//                } else {
//                    self.fs.as_ref().unwrap().exists(&path).await
//                }
//            })
//            .unwrap())
//    }
//
//    pub fn generate_presigned_url(&mut self, path: PathBuf, expiration: u64) -> PyResult<String> {
//        Ok(self
//            .runtime
//            .block_on(async {
//                if self.client_mode {
//                    self.http
//                        .as_mut()
//                        .unwrap()
//                        .generate_presigned_url(&path)
//                        .await
//                } else {
//                    self.fs
//                        .as_ref()
//                        .unwrap()
//                        .generate_presigned_url(&path, expiration)
//                        .await
//                }
//            })
//            .unwrap())
//    }
//}

#[cfg(test)]
mod tests {
    use super::*;

    use opsml_settings::config::OpsmlConfig;
    use rand::distributions::Alphanumeric;
    use rand::thread_rng;
    use rand::Rng;
    use std::fs::File;
    use std::io::Write;

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

    #[tokio::test]
    async fn test_gcs_storage_client() {
        let config = OpsmlConfig::new(Some(true));

        let mut client = FileSystemStorage::new(&mut config.storage_settings())
            .await
            .unwrap();

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
    }

    #[tokio::test]
    async fn test_aws_storage_client() {
        let config = OpsmlConfig::new(Some(true));

        let mut client = FileSystemStorage::new(&mut config.storage_settings())
            .await
            .unwrap();

        assert_eq!(client.name(), "HttpFSStorageClient");
        assert_eq!(client.storage_type(), StorageType::AWS);

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
        let config = OpsmlConfig::new(Some(true));

        let mut client = FileSystemStorage::new(&mut config.storage_settings())
            .await
            .unwrap();

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
        let config = OpsmlConfig::new(Some(true));

        let mut client = FileSystemStorage::new(&mut config.storage_settings())
            .await
            .unwrap();

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
    }
}
