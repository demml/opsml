use crate::storage::error::StorageError;
use crate::storage::http::multipart::MultiPartUploader;
use crate::storage::utils::set_download_chunk_size;
use opsml_client::OpsmlApiClient;
use opsml_client::error::ApiClientError;
use opsml_colors::Colorize;
use opsml_types::api::{RequestType, Routes};
use opsml_types::{StorageType, contracts::*};
use std::io::{Read, Write};
use std::path::Path;
use std::sync::Arc;
use tracing::{error, instrument};

#[derive(Clone)]
pub struct HttpStorageClient {
    pub api_client: Arc<OpsmlApiClient>,
    pub storage_type: StorageType,
}

impl HttpStorageClient {
    pub fn new(api_client: Arc<OpsmlApiClient>) -> Result<Self, StorageError> {
        let storage_type = Self::get_storage_setting(api_client.clone())?;

        Ok(Self {
            api_client,
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
    fn get_storage_setting(client: Arc<OpsmlApiClient>) -> Result<StorageType, StorageError> {
        let response = client
            .request(Routes::StorageSettings, RequestType::Get, None, None, None)
            .inspect_err(|e| {
                let error = Colorize::alert(&format!("Failed to get storage settings: {e}"));
                error!("{}", error);
            })?;

        let settings = response
            .json::<StorageSettings>()
            .map_err(ApiClientError::RequestError)?;

        Ok(settings.storage_type)
    }

    #[instrument(skip_all)]
    pub fn find(&self, path: &str) -> Result<Vec<String>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)?;

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
            .inspect_err(|e| {
                error!("Failed to get files: {e}");
            })?;

        let response = response.json::<ListFileResponse>()?;

        Ok(response.files)
    }

    #[instrument(skip_all)]
    pub fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
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
            .inspect_err(|e| {
                error!("Failed to get files: {e}");
            })?;

        let response = response.json::<ListFileInfoResponse>()?;

        Ok(response.files)
    }

    #[instrument(skip_all)]
    pub fn get_object(
        &self,
        local_path: &str,
        remote_path: &str,
        file_size: i64,
    ) -> Result<(), StorageError> {
        // check if local path exists, create it if it doesn't
        let local_path = Path::new(local_path);

        if !local_path.exists() {
            std::fs::create_dir_all(local_path.parent().unwrap())?;
        }

        // create local file
        let mut file = std::fs::File::create(local_path)?;

        // generate presigned url for downloading the object
        let presigned_url = self.generate_presigned_url(remote_path)?;

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

            self.api_client.client.get(url).send().unwrap()
        };

        // create buffer to store downloaded data
        let mut reader = response;
        let mut buffer = vec![0; set_download_chunk_size(file_size as u64, None)];

        loop {
            let bytes_read = reader.read(&mut buffer).inspect_err(|e| {
                error!("Failed to read from response: {e}");
            })?;

            if bytes_read == 0 {
                break;
            }

            file.write_all(&buffer[..bytes_read]).inspect_err(|e| {
                error!("Failed to write chunk: {e}");
            })?;
        }

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn delete_object(&self, path: &str) -> Result<bool, StorageError> {
        let query = DeleteFileQuery {
            path: path.to_string(),
            recursive: false,
        };

        let query_string = serde_qs::to_string(&query)?;

        let response = self
            .api_client
            .request(
                Routes::DeleteFiles,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to delete file: {e}");
            })?;

        let response = response.json::<DeleteFileResponse>().inspect_err(|e| {
            error!("Failed to parse delete response: {e}");
        })?;

        Ok(response.deleted)
    }

    pub fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let query = DeleteFileQuery {
            path: path.to_string(),
            recursive: true,
        };

        let query_string = serde_qs::to_string(&query)?;

        let response = self
            .api_client
            .request(
                Routes::DeleteFiles,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to delete file: {e}");
            })?;

        let response = response.json::<DeleteFileResponse>()?;

        Ok(response.deleted)
    }

    #[instrument(skip_all)]
    pub fn create_multipart_upload(&self, path: &str) -> Result<MultiPartSession, StorageError> {
        // 1 - create multipart upload request and send to server
        let query = MultiPartQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)?;

        let response = self
            .api_client
            .request(
                Routes::Multipart,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to create multipart upload: {e}");
            })?;

        // check if unauthorized
        if response.status().is_client_error() {
            let error_resp = response.json::<PermissionDenied>()?;
            return Err(ApiClientError::PermissionDeniedError(error_resp.error).into());
        }

        // deserialize response into MultiPartSession
        let session = response.json::<MultiPartSession>()?;

        // return session url
        // For GCS - this returns the resumable upload session url
        // For AWS - this returns the upload_id for a multipart upload
        // for Azure - this is the presigned url for a block upload
        Ok(session)
    }

    /// Create a multipart uploader based on configured storage type
    pub fn create_multipart_uploader(
        &self,
        rpath: &Path,
        lpath: &Path,
    ) -> Result<MultiPartUploader, StorageError> {
        // 1 get session url from server
        let multipart_session = self
            .create_multipart_upload(rpath.to_str().unwrap())
            .inspect_err(|e| {
                error!("Failed to create multipart upload: {e}");
            })?;

        Ok(MultiPartUploader::new(
            rpath,
            lpath,
            &self.storage_type,
            self.api_client.clone(),
            multipart_session.session_url,
        )?)
    }

    #[instrument(skip_all)]
    pub fn generate_presigned_url(&self, path: &str) -> Result<String, StorageError> {
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
            .inspect_err(|e| {
                error!("Failed to generate presigned url: {e}");
            })?;

        let response = response.json::<PresignedUrl>().inspect_err(|e| {
            error!("Failed to parse presigned url response: {e}");
        })?;

        Ok(response.url)
    }
}
