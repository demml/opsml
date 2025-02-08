use crate::storage::enums::client::{MultiPartUploader, StorageClientEnum};
use anyhow::{Context, Result as AnyhowResult};
use bytes::BytesMut;
use indicatif::{ProgressBar, ProgressStyle};
use opsml_client::{OpsmlApiClient, RequestType, Routes};
use opsml_colors::Colorize;
use opsml_error::error::ApiError;
use opsml_error::error::StorageError;
use opsml_settings::config::{ApiSettings, OpsmlStorageSettings};
use opsml_types::{contracts::*, StorageType, DOWNLOAD_CHUNK_SIZE};

use reqwest::{
    header::{HeaderMap, HeaderValue},
    Client,
};
use serde_json::Value;
use std::io::Write;
use std::path::Path;
use tracing::{error, instrument};

const TIMEOUT_SECS: u64 = 30;

/// Create a new HTTP client that can be shared across different clients
pub fn build_http_client(settings: &ApiSettings) -> Result<Client, ApiError> {
    let mut headers = HeaderMap::new();
    headers.insert(
        "X-Prod-Token",
        HeaderValue::from_str(settings.prod_token.as_deref().unwrap_or(""))
            .map_err(|e| ApiError::Error(format!("Failed to create header with error: {}", e)))?,
    );

    let client_builder = Client::builder().timeout(std::time::Duration::from_secs(TIMEOUT_SECS));
    let client = client_builder
        .default_headers(headers)
        .build()
        .map_err(|e| ApiError::Error(format!("Failed to create client with error: {}", e)))?;
    Ok(client)
}

#[derive(Clone)]
pub struct HttpStorageClient {
    pub api_client: OpsmlApiClient,
    storage_client: StorageClientEnum,
    pub storage_type: StorageType,
}

impl HttpStorageClient {
    pub async fn new(settings: &mut OpsmlStorageSettings, client: &Client) -> AnyhowResult<Self> {
        let mut api_client = OpsmlApiClient::new(settings, client)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to create api client: {}", e)))
            .context(Colorize::purple("Error occurred while creating api client"))?;

        // get storage type from opsml_server

        let storage_type =
            Self::get_storage_setting(&mut api_client)
                .await
                .context(Colorize::purple(
                    "Error occurred while getting storage type",
                ))?;

        // update settings type
        settings.storage_type = storage_type.clone();

        // get storage client (options are gcs, aws, azure and local)
        let storage_client = StorageClientEnum::new(settings)
            .await
            .map_err(|e| StorageError::Error(format!("Failed to create storage client: {}", e)))
            .context(Colorize::green(
                "Error occurred while creating storage client",
            ))?;

        Ok(Self {
            api_client,
            storage_client,
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
    #[instrument(skip(client))]
    async fn get_storage_setting(client: &mut OpsmlApiClient) -> Result<StorageType, StorageError> {
        let response = client
            .request_with_retry(Routes::StorageSettings, RequestType::Get, None, None, None)
            .await
            .map_err(|e| {
                let error = Colorize::alert(&format!("Failed to get storage settings: {}", e));
                error!("{}", error);
                StorageError::Error(error)
            })?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        // convert Value to Vec<String>
        let settings = serde_json::from_value::<StorageSettings>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

        Ok(settings.storage_type)
    }

    #[instrument(skip(self, path))]
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
            .request_with_retry(
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

        let val = response.json::<Value>().await.map_err(|e| {
            error!("Failed to parse response: {}", e);
            StorageError::Error(format!("Failed to parse response: {}", e))
        })?;

        // convert Value to Vec<String>
        let response = serde_json::from_value::<ListFileResponse>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

        Ok(response.files)
    }

    #[instrument(skip(self, path))]
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
            .request_with_retry(
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

        let val = response.json::<Value>().await.map_err(|e| {
            error!("Failed to parse response: {}", e);
            StorageError::Error(format!("Failed to parse response: {}", e))
        })?;

        let response = serde_json::from_value::<ListFileInfoResponse>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

        Ok(response.files)
    }

    #[instrument(skip(self, local_path, remote_path))]
    pub async fn get_object(
        &mut self,
        local_path: &str,
        remote_path: &str,
        file_size: i64,
    ) -> Result<(), StorageError> {
        // check if local path exists, create it if it doesn't
        let local_path = Path::new(local_path);

        if !local_path.exists() {
            std::fs::create_dir_all(local_path.parent().unwrap()).map_err(|e| {
                error!("Failed to create directory: {}", e);
                StorageError::Error(format!("Failed to create directory: {}", e))
            })?;
        }

        let chunk_count = ((file_size / DOWNLOAD_CHUNK_SIZE as i64) + 1) as u64;

        let bar = ProgressBar::new(chunk_count);

        let msg1 = Colorize::green("Downloading file:");
        let msg2 = Colorize::purple(local_path.file_name().unwrap().to_string_lossy().as_ref());

        let msg = format!("{} {}", msg1, msg2);
        let template = format!(
            "{} [{{bar:40.green/magenta}}] {{pos}}/{{len}} ({{eta}})",
            msg
        );

        let style = ProgressStyle::with_template(&template)
            .unwrap()
            .progress_chars("#--");
        bar.set_style(style);

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
                .request_with_retry(
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

            self.api_client.client.get(url).send().await.unwrap()
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
                bar.inc(1);
            }
        }

        // Write any remaining data in the buffer
        if !buffer.is_empty() {
            file.write_all(&buffer).map_err(|e| {
                error!("Failed to write remaining data: {}", e);
                StorageError::Error(format!("Failed to write remaining data: {}", e))
            })?;
        }

        bar.finish_with_message("Download complete");
        Ok(())
    }

    #[instrument(skip(self, path))]
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
            .request_with_retry(
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

        let val = response.json::<Value>().await.map_err(|e| {
            error!("Failed to parse response: {}", e);
            StorageError::Error(format!("Failed to parse response: {}", e))
        })?;

        // load DeleteFileResponse from response
        let response = serde_json::from_value::<DeleteFileResponse>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

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
            .request_with_retry(
                Routes::DeleteFiles,
                RequestType::Delete,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| StorageError::Error(format!("Failed to delete file: {}", e)))?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        let response = serde_json::from_value::<DeleteFileResponse>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(response.deleted)
    }

    #[instrument(skip(self, path))]
    pub async fn create_multipart_upload(&mut self, path: &str) -> Result<String, StorageError> {
        let query = MultiPartQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query).map_err(|e| {
            error!("Failed to serialize query: {}", e);
            StorageError::Error(format!("Failed to serialize query: {}", e))
        })?;

        let response = self
            .api_client
            .request_with_retry(
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

        // deserialize response into MultiPartSession
        let val = response.json::<Value>().await.map_err(|e| {
            error!("Failed to parse response: {}", e);
            StorageError::Error(format!("Failed to parse response: {}", e))
        })?;

        let session = serde_json::from_value::<MultiPartSession>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

        let session_url = session.session_url;

        Ok(session_url.to_string())
    }

    /// Create a multipart uploader based on configured storage type
    pub async fn create_multipart_uploader(
        &mut self,
        rpath: &Path,
        lpath: &Path,
    ) -> Result<MultiPartUploader, StorageError> {
        let session_url = self
            .create_multipart_upload(rpath.to_str().unwrap())
            .await?;

        let uploader = self
            .storage_client
            .create_multipart_uploader(lpath, rpath, session_url, Some(self.api_client.clone()))
            .await?;

        Ok(uploader)
    }

    #[instrument(skip(self, path))]
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
            .request_with_retry(
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

        let val = response.json::<Value>().await.map_err(|e| {
            error!("Failed to parse response: {}", e);
            StorageError::Error(format!("Failed to parse response: {}", e))
        })?;

        let response = serde_json::from_value::<PresignedUrl>(val).map_err(|e| {
            error!("Failed to deserialize response: {}", e);
            StorageError::Error(format!("Failed to deserialize response: {}", e))
        })?;

        Ok(response.url)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockito::{Server, ServerGuard};
    use opsml_settings::config::OpsmlConfig;
    use tokio;

    async fn setup_server() -> (ServerGuard, String) {
        let server = Server::new_async().await;
        let server_url = server.url();
        (server, server_url)
    }

    async fn setup_client(server_url: String, use_auth: Option<bool>) -> OpsmlApiClient {
        let config = OpsmlConfig::new(None);
        let mut settings = config.storage_settings();

        // set up some auth
        settings.api_settings.username = "username".to_string();
        settings.api_settings.password = "password".to_string();
        settings.api_settings.use_auth = use_auth.unwrap_or(false);
        settings.api_settings.base_url = server_url.to_string();

        let client = build_http_client(&settings.api_settings).unwrap();
        OpsmlApiClient::new(&settings, &client).await.unwrap()
    }

    #[tokio::test]
    async fn test_api_client_no_auth() {
        let (mut server, server_url) = setup_server().await;
        let mut api_client = setup_client(server_url, None).await;

        let _mock = server
            .mock("GET", "/opsml/files")
            .with_status(200)
            .with_body(r#"{"status": "ok"}"#)
            .create();

        let response = api_client
            .request_with_retry(Routes::Files, RequestType::Get, None, None, None)
            .await
            .unwrap();

        assert_eq!(response.status(), 200);
    }

    #[tokio::test]
    async fn test_api_client_with_auth() {
        let (mut server, server_url) = setup_server().await;

        // Mock auth token endpoint
        let _token_mock = server
            .mock("POST", "/opsml/auth/token")
            .with_status(200)
            .with_body(r#"{"access_token": "test_token"}"#)
            .expect(1)
            .create();

        // Mock protected endpoint
        let _protected_mock = server
            .mock("GET", "/opsml/files")
            .match_header("Authorization", "Bearer test_token")
            .with_status(200)
            .with_body(r#"{"status": "authenticated"}"#)
            .expect(1)
            .create();

        let mut api_client = setup_client(server_url, Some(true)).await;

        let response = api_client
            .request_with_retry(Routes::Files, RequestType::Get, None, None, None)
            .await
            .unwrap();

        assert_eq!(response.status(), 200);
    }

    #[tokio::test]
    async fn test_request_with_retry_success() {
        let (mut server, server_url) = setup_server().await;

        // Mock auth token endpoint
        let _token_mock = server
            .mock("POST", "/opsml/auth/token")
            .with_status(200)
            .with_body(r#"{"access_token": "test_token"}"#)
            .expect(1)
            .create();

        // Mock endpoint that succeeds
        let _success_mock = server
            .mock("GET", "/opsml/files")
            .match_header("Authorization", "Bearer test_token")
            .with_status(200)
            .with_body(r#"{"status": "success"}"#)
            .expect(1)
            .create();

        let mut api_client = setup_client(server_url, Some(true)).await;

        let response = api_client
            .request_with_retry(Routes::Files, RequestType::Get, None, None, None)
            .await
            .unwrap();

        assert_eq!(response.status(), 200);
    }

    #[tokio::test]
    async fn test_request_with_retry_failure() {
        let (mut server, server_url) = setup_server().await;

        // Mock auth token endpoint - will be called multiple times
        let _token_mock = server
            .mock("POST", "/opsml/auth/token")
            .with_status(200)
            .with_body(r#"{"access_token": "test_token"}"#)
            .expect(3)
            .create();

        // Mock endpoint that fails with 401 three times
        let _failure_mock = server
            .mock("GET", "/opsml/files")
            .match_header("Authorization", "Bearer test_token")
            .with_status(401)
            .expect(3)
            .create();

        let mut api_client = setup_client(server_url, Some(true)).await;
        let result = api_client
            .request_with_retry(Routes::Files, RequestType::Get, None, None, None)
            .await;

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_request_with_retry_auth_refresh() {
        let (mut server, server_url) = setup_server().await;

        // Mock auth token endpoint - first token
        let _initial_token_mock = server
            .mock("POST", "/opsml/auth/token")
            .with_status(200)
            .with_body(r#"{"access_token": "initial_token"}"#)
            .expect(1)
            .create();

        // Mock auth token endpoint - refresh token
        let _refresh_token_mock = server
            .mock("POST", "/opsml/auth/token")
            .with_status(200)
            .with_body(r#"{"access_token": "refreshed_token"}"#)
            .expect(1)
            .create();

        // Mock protected endpoint - first attempt fails with 401
        let _first_attempt_mock = server
            .mock("GET", "/opsml/test")
            .match_header("Authorization", "Bearer initial_token")
            .with_status(401)
            .expect(1)
            .create();

        // Mock protected endpoint - second attempt succeeds with new token
        let _second_attempt_mock = server
            .mock("GET", "/opsml/files")
            .match_header("Authorization", "Bearer refreshed_token")
            .with_status(200)
            .with_body(r#"{"status": "success_after_refresh"}"#)
            .expect(1)
            .create();

        let mut api_client = setup_client(server_url, Some(true)).await;

        let response = api_client
            .request_with_retry(Routes::Files, RequestType::Get, None, None, None)
            .await
            .unwrap();

        assert_eq!(response.status(), 200);

        _first_attempt_mock.assert();
        _second_attempt_mock.assert();
        _initial_token_mock.assert();
        _refresh_token_mock.assert();
    }
}
