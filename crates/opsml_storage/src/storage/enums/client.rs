/// Implements a generic enum to handle different storage clients based on the storage URI
/// This enum is meant to provide a common interface to use in the server
use crate::storage::filesystem::FileSystem;
use crate::storage::local::client::{LocalFSStorageClient, LocalMultiPartUpload};

use crate::storage::aws::client::{AWSMulitPartUpload, S3FStorageClient};
use crate::storage::azure::client::{AzureFSStorageClient, AzureMultipartUpload};
use crate::storage::error::StorageError;
use crate::storage::gcs::client::{GCSFSStorageClient, GoogleMultipartUpload};
use anyhow::{Context, Result as AnyhowResult};
use opsml_settings::config::{OpsmlConfig, OpsmlStorageSettings};
use opsml_types::StorageType;
use opsml_types::contracts::CompleteMultipartUpload;
use opsml_types::contracts::FileInfo;
use opsml_utils::ChunkParts;
use std::path::Path;
use tracing::{debug, instrument};

pub enum MultiPartUploader {
    Google(GoogleMultipartUpload),
    AWS(AWSMulitPartUpload),
    Local(LocalMultiPartUpload),
    Azure(AzureMultipartUpload),
}

impl MultiPartUploader {
    pub fn session_url(&self) -> String {
        match self {
            MultiPartUploader::Google(uploader) => uploader.upload_client.url().to_string(),
            MultiPartUploader::AWS(uploader) => uploader.upload_id.clone(),
            MultiPartUploader::Local(uploader) => {
                uploader.rpath.clone().to_str().unwrap().to_string()
            }
            MultiPartUploader::Azure(uploader) => uploader.signed_url.clone(),
        }
    }

    pub async fn upload_file_in_chunks(
        &mut self,
        chunk_parts: ChunkParts,
    ) -> Result<(), StorageError> {
        match self {
            MultiPartUploader::Google(uploader) => {
                Ok(uploader.upload_file_in_chunks(chunk_parts).await?)
            }
            MultiPartUploader::AWS(uploader) => {
                Ok(uploader.upload_file_in_chunks(chunk_parts).await?)
            }

            MultiPartUploader::Local(uploader) => Ok(uploader.upload_file_in_chunks().await?),
            MultiPartUploader::Azure(uploader) => {
                Ok(uploader.upload_file_in_chunks(chunk_parts).await?)
            }
        }
    }
}

#[derive(Clone)]
pub enum StorageClientEnum {
    Google(GCSFSStorageClient),
    AWS(S3FStorageClient),
    Local(LocalFSStorageClient),
    Azure(AzureFSStorageClient),
}

impl StorageClientEnum {
    pub fn bucket(&self) -> &str {
        match self {
            StorageClientEnum::Google(client) => client.bucket(),
            StorageClientEnum::AWS(client) => client.bucket(),
            StorageClientEnum::Local(client) => client.bucket(),
            StorageClientEnum::Azure(client) => client.bucket(),
        }
    }
    pub fn name(&self) -> &str {
        match self {
            StorageClientEnum::Google(client) => client.name(),
            StorageClientEnum::AWS(client) => client.name(),
            StorageClientEnum::Local(client) => client.name(),
            StorageClientEnum::Azure(client) => client.name(),
        }
    }

    pub fn storage_type(&self) -> StorageType {
        match self {
            StorageClientEnum::Google(_) => StorageType::Google,
            StorageClientEnum::AWS(_) => StorageType::Aws,
            StorageClientEnum::Local(_) => StorageType::Local,
            StorageClientEnum::Azure(_) => StorageType::Azure,
        }
    }

    #[instrument(skip_all)]
    pub async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError> {
        match settings.storage_type {
            StorageType::Google => {
                // strip the gs:// prefix
                let client = GCSFSStorageClient::new(settings).await;
                Ok(StorageClientEnum::Google(client))
            }

            StorageType::Aws => {
                // strip the s3:// prefix
                let client = S3FStorageClient::new(settings).await;
                Ok(StorageClientEnum::AWS(client))
            }
            StorageType::Local => {
                let client = LocalFSStorageClient::new(settings).await;
                Ok(StorageClientEnum::Local(client))
            }

            StorageType::Azure => {
                let client = AzureFSStorageClient::new(settings).await;
                Ok(StorageClientEnum::Azure(client))
            }
        }
    }
    #[instrument(skip_all)]
    pub async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.find(path).await,
            StorageClientEnum::AWS(client) => client.find(path).await,
            StorageClientEnum::Local(client) => client.find(path).await,
            StorageClientEnum::Azure(client) => client.find(path).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.find_info(path).await,
            StorageClientEnum::AWS(client) => client.find_info(path).await,
            StorageClientEnum::Local(client) => client.find_info(path).await,
            StorageClientEnum::Azure(client) => client.find_info(path).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn get(
        &self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.get(lpath, rpath, recursive).await,
            StorageClientEnum::AWS(client) => client.get(lpath, rpath, recursive).await,
            StorageClientEnum::Local(client) => client.get(lpath, rpath, recursive).await,
            StorageClientEnum::Azure(client) => client.get(lpath, rpath, recursive).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn put(
        &self,
        lpath: &Path,
        rpath: &Path,
        recursive: bool,
    ) -> Result<(), StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.put(lpath, rpath, recursive).await,
            StorageClientEnum::AWS(client) => client.put(lpath, rpath, recursive).await,
            StorageClientEnum::Local(client) => client.put(lpath, rpath, recursive).await,
            StorageClientEnum::Azure(client) => client.put(lpath, rpath, recursive).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.copy(src, dest, recursive).await,
            StorageClientEnum::AWS(client) => client.copy(src, dest, recursive).await,
            StorageClientEnum::Local(client) => client.copy(src, dest, recursive).await,
            StorageClientEnum::Azure(client) => client.copy(src, dest, recursive).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.rm(path, recursive).await,
            StorageClientEnum::AWS(client) => client.rm(path, recursive).await,
            StorageClientEnum::Local(client) => client.rm(path, recursive).await,
            StorageClientEnum::Azure(client) => client.rm(path, recursive).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.exists(path).await,
            StorageClientEnum::AWS(client) => client.exists(path).await,
            StorageClientEnum::Local(client) => client.exists(path).await,
            StorageClientEnum::Azure(client) => client.exists(path).await,
        }
    }

    #[instrument(skip_all)]
    pub async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        match self {
            StorageClientEnum::Google(client) => {
                client.generate_presigned_url(path, expiration).await
            }
            StorageClientEnum::AWS(client) => client.generate_presigned_url(path, expiration).await,
            StorageClientEnum::Local(client) => {
                client.generate_presigned_url(path, expiration).await
            }
            StorageClientEnum::Azure(client) => {
                client.generate_presigned_url(path, expiration).await
            }
        }
    }

    pub async fn generate_presigned_url_for_part(
        &self,
        part_number: i32,
        path: &Path,
        session_url: String,
    ) -> Result<String, StorageError> {
        match self {
            StorageClientEnum::Google(_client) => Ok(session_url),

            StorageClientEnum::AWS(client) => Ok(client
                .generate_presigned_url_for_part(part_number, path, &session_url)
                .await?),
            StorageClientEnum::Local(_client) => Ok(session_url),
            StorageClientEnum::Azure(_client) => Ok(session_url),
        }
    }

    pub async fn create_multipart_upload(&self, path: &Path) -> Result<String, StorageError> {
        match self {
            StorageClientEnum::Google(client) => {
                // google returns the session uri
                let result = client.create_multipart_upload(path).await?;
                Ok(result.url().to_string())
            }

            StorageClientEnum::AWS(client) => {
                // aws returns the session uri
                Ok(client.create_multipart_upload(path).await?)
            }
            StorageClientEnum::Local(client) => {
                // local returns the path
                debug!("Local create_multipart_upload: {:?}", path);
                client.create_multipart_upload(path).await
            }

            StorageClientEnum::Azure(client) => {
                // azure returns the session uri
                Ok(client.create_multipart_upload(path).await?)
            }
        }
    }

    pub async fn create_multipart_uploader(
        &self,
        lpath: &Path,
        rpath: &Path,
    ) -> Result<MultiPartUploader, StorageError> {
        match self {
            StorageClientEnum::Google(client) => {
                let uploader = client.create_multipart_uploader(lpath, rpath).await?;
                Ok(MultiPartUploader::Google(uploader))
            }

            StorageClientEnum::AWS(client) => {
                let uploader = client.create_multipart_uploader(rpath, lpath).await?;
                Ok(MultiPartUploader::AWS(uploader))
            }
            StorageClientEnum::Local(client) => {
                let uploader = client.create_multipart_uploader(lpath, rpath).await?;

                Ok(MultiPartUploader::Local(uploader))
            }
            StorageClientEnum::Azure(client) => {
                let uploader = client.create_multipart_uploader(lpath, rpath).await?;
                Ok(MultiPartUploader::Azure(uploader))
            }
        }
    }

    pub async fn complete_multipart_upload(
        &self,
        request: CompleteMultipartUpload,
    ) -> Result<(), StorageError> {
        match self {
            StorageClientEnum::Google(client) => client.complete_multipart_upload(request).await,
            StorageClientEnum::AWS(client) => client.complete_multipart_upload(request).await,
            StorageClientEnum::Local(client) => client.complete_multipart_upload(request).await,
            StorageClientEnum::Azure(client) => client.complete_multipart_upload(request).await,
        }
    }
}

pub async fn get_storage_system(config: &OpsmlConfig) -> AnyhowResult<StorageClientEnum> {
    // check storage_uri for prefix
    let storage_settings = config.storage_settings().with_context(|| {
        format!(
            "Failed to get storage settings from config: {:?}",
            config.storage_settings()
        )
    })?;

    StorageClientEnum::new(&storage_settings)
        .await
        .with_context(|| {
            format!(
                "Failed to create storage client for storage type: {:?}",
                storage_settings.storage_type
            )
        })
}
//
//#[pyfunction]
//pub fn get_opsml_storage_system(config: &OpsmlConfig) -> AnyhowResult<PyStorageClient> {
//    // check storage_uri for prefix
//    let storage_settings = config.storage_settings();
//
//    PyStorageClient::new(&storage_settings).with_context(|| {
//        format!(
//            "Failed to create storage client for storage type: {:?}",
//            storage_settings.storage_type
//        )
//    })
//}
