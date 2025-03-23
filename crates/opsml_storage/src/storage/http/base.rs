use crate::storage::enums::client::{MultiPartUploader, StorageClientEnum};
use anyhow::{Context, Result as AnyhowResult};
use bytes::BytesMut;
use opsml_client::{build_api_client, get_api_client, OpsmlApiClient, RequestType, Routes};
use opsml_colors::Colorize;
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::{contracts::*, StorageType, DOWNLOAD_CHUNK_SIZE};
use std::io::Write;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{error, instrument};

#[derive(Clone)]
pub struct HttpStorageClient {
    pub api_client: Arc<OpsmlApiClient>,
    //storage_client: StorageClientEnum,
    pub storage_type: StorageType,
}

impl HttpStorageClient {
    pub async fn new(api_client: Arc<OpsmlApiClient>) -> AnyhowResult<Self> {
        let storage_type = Self::get_storage_setting().await.context(Colorize::purple(
            "Error occurred while getting storage type",
        ))?;

        // get storage client (options are gcs, aws, azure and local)
        //let storage_client = StorageClientEnum::new(settings)
        //    .await
        //    .map_err(|e| StorageError::Error(format!("Failed to create storage client: {}", e)))
        //    .context(Colorize::green(
        //        "Error occurred while creating storage client",
        //    ))?;

        Ok(Self {
            api_client: api_client,
            //storage_client,
            storage_type,
        })
    }

    /// Function used to get the storage type from the server.
    /// A storage client is needed for when uploading and downloading files via presigned urls.
    ///
    /// # Arguments
    ///
    /// * `client` - The OpsmlApiClient
    ///
    /// # Returns
    ///
    /// * `StorageType` - The storage type
    #[instrument(skip_all)]
    async fn get_storage_setting() -> Result<StorageType, StorageError> {
        let mut client = get_api_client().lock().await;
        let response = client
            .request(Routes::StorageSettings, RequestType::Get, None, None, None)
            .await
            .map_err(|e| {
                let error = Colorize::alert(&format!("Failed to get storage settings: {}", e));
                error!("{}", error);
                StorageError::Error(error)
            })?;

        let settings = response
            .json::<StorageSettings>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse storage response: {}", e)))?;

        // convert Value to Vec<String>
        //let settings = serde_json::from_value::<StorageSettings>(val).map_err(|e| {
        //    error!("Failed to deserialize response: {}", e);
        //    StorageError::Error(format!("Failed to deserialize response: {}", e))
        //})?;

        Ok(settings.storage_type)
    }

    #[instrument(skip_all)]
    pub async fn find(&mut self, path: &str) -> Result<Vec<String>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        // need to clone because self is borrowed
        let response = self
            .api_client
            .request(
                Routes::List,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to get files: {}", e);
                StorageError::Error(format!("Failed to get files: {}", e))
            })?;

        let response = response.json::<ListFileResponse>().await.map_err(|e| {
            error!("Failed to parse list file response: {}", e);
            StorageError::Error(format!("Failed to parse list file response: {}", e))
        })?;

        // convert Value to Vec<String>
        //let response = serde_json::from_value::<ListFileResponse>(val).map_err(|e| {
        //    error!("Failed to deserialize response: {}", e);
        //    StorageError::Error(format!("Failed to deserialize response: {}", e))
        //})?;

        Ok(response.files)
    }

    #[instrument(skip_all)]
    pub async fn find_info(&mut self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        let response = self
            .api_client
            .request(
                Routes::ListInfo,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to get files: {}", e);
                StorageError::Error(format!("Failed to get files: {}", e))
            })?;

        let response = response.json::<ListFileInfoResponse>().await.map_err(|e| {
            error!("Failed to parse file info response: {}", e);
            StorageError::Error(format!("Failed to parse file info response: {}", e))
        })?;

        //let response = serde_json::from_value::<ListFileInfoResponse>(val).map_err(|e| {
        //    error!("Failed to deserialize response: {}", e);
        //    StorageError::Error(format!("Failed to deserialize response: {}", e))
        //})?;

        Ok(response.files)
    }

    #[instrument(skip_all)]
    pub async fn get_object(
        &mut self,
        local_path: &str,
        remote_path: &str,
        _file_size: i64,
    ) -> Result<(), StorageError> {
        // check if local path exists, create it if it doesn't
        let local_path = Path::new(local_path);

        if !local_path.exists() {
            std::fs::create_dir_all(local_path.parent().unwrap()).map_err(|e| {
                error!("Failed to create directory: {}", e);
                StorageError::Error(format!("Failed to create directory: {}", e))
            })?;
        }

        // create local file
        let mut file = std::fs::File::create(local_path).map_err(|e| {
            error!("Failed to create file: {}", e);
            StorageError::Error(format!("Failed to create file: {}", e))
        })?;

        // generate presigned url for downloading the object
        let presigned_url = self.generate_presigned_url(remote_path).await?;

        // download the object
        let mut response = if self.storage_type == StorageType::Local {
            let query = DownloadFileQuery {
                path: remote_path.to_string(),
            };

            let query_string = serde_qs::to_string(&query).map_err(|e| {
                error!("Failed to serialize query: {}", e);
                StorageError::Error(format!("Failed to serialize query: {}", e))
            })?;

            self.api_client
                .lock()
                .await
                .request(
                    Routes::Files,
                    RequestType::Get,
                    None,
                    Some(query_string),
                    None,
                )
                .await
                .map_err(|e| {
                    error!("Failed to get file: {}", e);
                    StorageError::Error(format!("Failed to get file: {}", e))
                })?
        } else {
            // if storage clients are gcs, aws and azure, use presigned url to download the object
            // If local storage client, download the object from api route
            let url = reqwest::Url::parse(&presigned_url).map_err(|e| {
                error!("Invalid presigned URL: {}", e);
                StorageError::Error(format!("Invalid presigned URL: {}", e))
            })?;

            self.api_client
                .lock()
                .await
                .client
                .get(url)
                .send()
                .await
                .unwrap()
        };

        // create buffer to store downloaded data
        let mut buffer = BytesMut::with_capacity(DOWNLOAD_CHUNK_SIZE);

        // download the object in chunks
        while let Some(chunk) = response.chunk().await.map_err(|e| {
            error!("Failed to get chunk from response: {}", e);
            StorageError::Error(format!("Failed to get chunk from response: {}", e))
        })? {
            buffer.extend_from_slice(&chunk);
            if buffer.len() >= DOWNLOAD_CHUNK_SIZE {
                file.write_all(&buffer).map_err(|e| {
                    error!("Failed to write chunk: {}", e);
                    StorageError::Error(format!("Failed to write chunk: {}", e))
                })?;
                buffer.clear();
            }
        }

        // Write any remaining data in the buffer
        if !buffer.is_empty() {
            file.write_all(&buffer).map_err(|e| {
                error!("Failed to write remaining data: {}", e);
                StorageError::Error(format!("Failed to write remaining data: {}", e))
            })?;
        }

        Ok(())
    }

    #[instrument(skip_all)]
    pub async fn delete_object(&mut self, path: &str) -> Result<bool, StorageError> {
        let query = DeleteFileQuery {
            path: path.to_string(),
            recursive: false,
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        let response = self
            .api_client
            .lock()
            .await
            .request(
                Routes::DeleteFiles,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to delete file: {}", e);
                StorageError::Error(format!("Failed to delete file: {}", e))
            })?;

        let response = response.json::<DeleteFileResponse>().await.map_err(|e| {
            error!("Failed to parse delete response: {}", e);
            StorageError::Error(format!("Failed to parse delete response: {}", e))
        })?;

        // load DeleteFileResponse from response
        //let response = serde_json::from_value::<DeleteFileResponse>(val).map_err(|e| {
        //    error!("Failed to deserialize response: {}", e);
        //    StorageError::Error(format!("Failed to deserialize response: {}", e))
        //})?;

        Ok(response.deleted)
    }

    pub async fn delete_objects(&mut self, path: &str) -> Result<bool, StorageError> {
        let query = DeleteFileQuery {
            path: path.to_string(),
            recursive: true,
        };

        let query_string = serde_qs::to_string(&query)
            .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

        let response = self
            .api_client
            .lock()
            .await
            .request(
                Routes::DeleteFiles,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| StorageError::Error(format!("Failed to delete file: {}", e)))?;

        let response = response
            .json::<DeleteFileResponse>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse delete response: {}", e)))?;

        //let response = serde_json::from_value::<DeleteFileResponse>(val)
        //    .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(response.deleted)
    }

    #[instrument(skip_all)]
    pub async fn create_multipart_upload(
        &mut self,
        path: &str,
    ) -> Result<MultiPartSession, StorageError> {
        // 1 - create multipart upload request and send to server
        let query = MultiPartQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        let response = self
            .api_client
            .lock()
            .await
            .request(
                Routes::Multipart,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to create multipart upload: {}", e);
                StorageError::Error(format!("Failed to create multipart upload: {}", e))
            })?;

        // check if unauthorized
        if response.status().is_client_error() {
            let error_resp = response
                .json::<PermissionDenied>()
                .await
                .map_err(|e| StorageError::Error(e.to_string()))?;
            return Err(StorageError::PermissionDenied(error_resp.error));
        }

        // deserialize response into MultiPartSession
        let session = response.json::<MultiPartSession>().await.map_err(|e| {
            error!("Failed to parse multipart response: {}", e);
            StorageError::Error(e.to_string())
        })?;

        // return session url
        // For GCS - this returns the resumable upload session url
        // For AWS - this returns the upload_id for a multipart upload
        // for Azure - this is the presigned url for a block upload
        Ok(session)
    }

    /// Create a multipart uploader based on configured storage type
    pub async fn create_multipart_uploader(
        &mut self,
        rpath: &Path,
        lpath: &Path,
    ) -> Result<MultiPartUploader, StorageError> {
        // 1 get session url from server
        let multipart_session = self
            .create_multipart_upload(rpath.to_str().unwrap())
            .await
            .map_err(|e| {
                error!("Failed to create multipart upload: {}", e);
                StorageError::Error(format!("Failed to create multipart upload: {}", e))
            })?;

        // 2 create multipart uploader from url and api client
        // GCS - resumes resumable upload session given the session url
        // AWS - passes the session_url to AwsMUltipartUploaader
        // Azure - passes the session_url to AzureMultipartUploader
        let uploader = self
            .storage_client
            .create_multipart_uploader(lpath, rpath, multipart_session)
            .await
            .map_err(|e| {
                error!("Failed to create multipart uploader: {}", e);
                StorageError::Error(format!("Failed to create multipart uploader: {}", e))
            })?;

        Ok(uploader)
    }

    #[instrument(skip_all)]
    pub async fn generate_presigned_url(&mut self, path: &str) -> Result<String, StorageError> {
        let query = PresignedQuery {
            path: path.to_string(),
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        let response = self
            .api_client
            .lock()
            .await
            .request(
                Routes::Presigned,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| {
                error!("Failed to generate presigned url: {}", e);
                StorageError::Error(format!("Failed to generate presigned url: {}", e))
            })?;

        let response = response.json::<PresignedUrl>().await.map_err(|e| {
            error!("Failed to parse presigned response: {}", e);
            StorageError::Error(format!("Failed to parse presigned response: {}", e))
        })?;

        Ok(response.url)
    }
}
