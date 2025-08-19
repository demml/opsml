use crate::storage::error::StorageError;
use futures_util::StreamExt;
use opsml_client::error::ApiClientError;
use opsml_client::OpsmlApiAsyncClient;
use opsml_colors::Colorize;
use opsml_types::api::{RequestType, Routes};
use opsml_types::{contracts::*, StorageType};
use std::path::Path;
use std::sync::Arc;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;
use tracing::{error, instrument};

#[derive(Clone)]
pub struct AsyncHttpStorageClient {
    pub api_client: Arc<OpsmlApiAsyncClient>,
    pub storage_type: StorageType,
}

impl AsyncHttpStorageClient {
    pub async fn new(api_client: Arc<OpsmlApiAsyncClient>) -> Result<Self, StorageError> {
        let storage_type = Self::get_storage_setting(api_client.clone()).await?;

        Ok(Self {
            api_client,
            storage_type,
        })
    }

    #[instrument(skip_all)]
    pub async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)?;

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
            .inspect_err(|e| {
                error!("Failed to get files: {e}");
            })?;

        let response = response.json::<ListFileInfoResponse>().await?;

        Ok(response.files)
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
    async fn get_storage_setting(
        client: Arc<OpsmlApiAsyncClient>,
    ) -> Result<StorageType, StorageError> {
        let response = client
            .request(Routes::StorageSettings, RequestType::Get, None, None, None)
            .await
            .inspect_err(|e| {
                let error = Colorize::alert(&format!("Failed to get storage settings: {e}"));
                error!("{}", error);
            })?;

        let settings = response
            .json::<StorageSettings>()
            .await
            .map_err(ApiClientError::RequestError)?;

        Ok(settings.storage_type)
    }

    #[instrument(skip_all)]
    pub async fn get_object(
        &self,
        local_path: &str,
        remote_path: &str,
    ) -> Result<(), StorageError> {
        // check if local path exists, create it if it doesn't
        let local_path = Path::new(local_path);

        if !local_path.exists() {
            std::fs::create_dir_all(local_path.parent().unwrap())?;
        }

        // create local file
        let mut file = File::create(local_path).await?;

        // generate presigned url for downloading the object
        let presigned_url = self.generate_presigned_url(remote_path).await?;

        // download the object
        let response = if self.storage_type == StorageType::Local {
            let query = DownloadFileQuery {
                path: remote_path.to_string(),
            };

            let query_string = serde_qs::to_string(&query)?;

            self.api_client
                .request(
                    Routes::Files,
                    RequestType::Get,
                    None,
                    Some(query_string),
                    None,
                )
                .await
                .inspect_err(|e| {
                    error!("Failed to get file: {e}");
                })?
        } else {
            // if storage clients are gcs, aws and azure, use presigned url to download the object
            // If local storage client, download the object from api route
            let url = reqwest::Url::parse(&presigned_url).map_err(|e| {
                error!("Invalid presigned URL: {e}");
                StorageError::ParseUrlError(e.to_string())
            })?;

            self.api_client.client.get(url).send().await.unwrap()
        };

        // create buffer to store downloaded data
        let mut stream = response.bytes_stream();
        while let Some(chunk) = stream.next().await {
            let chunk = chunk.inspect_err(|e| {
                error!("Failed to read chunk from response: {e}");
            })?;
            file.write_all(&chunk).await.inspect_err(|e| {
                error!("Failed to write chunk: {e}");
            })?;
        }

        file.flush().await?;

        Ok(())
    }

    #[instrument(skip_all)]
    pub async fn generate_presigned_url(&self, path: &str) -> Result<String, StorageError> {
        let query = PresignedQuery {
            path: path.to_string(),
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&query)?;

        let response = self
            .api_client
            .request(
                Routes::Presigned,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .inspect_err(|e| {
                error!("Failed to generate presigned url: {e}");
            })?;

        let response = response.json::<PresignedUrl>().await?;

        Ok(response.url)
    }
}
