use crate::storage::enums::client::{MultiPartUploader, StorageClientEnum};
use anyhow::{Context, Result as AnyhowResult};
use bytes::BytesMut;
use indicatif::{ProgressBar, ProgressStyle};
use opsml_colors::Colorize;
use opsml_error::error::ApiError;
use opsml_error::error::StorageError;
use opsml_settings::config::{ApiSettings, OpsmlStorageSettings};
use opsml_types::{
    DeleteFileQuery, DeleteFileResponse, DownloadFileQuery, FileInfo, JwtToken,
    ListFileInfoResponse, ListFileQuery, ListFileResponse, MultiPartQuery, MultiPartSession,
    PresignedQuery, PresignedUrl, RequestType, Routes, StorageSettings, StorageType,
    DOWNLOAD_CHUNK_SIZE,
};
use reqwest::multipart::Form;
use reqwest::Response;
use reqwest::{
    header::{HeaderMap, HeaderValue},
    Client,
};
use serde_json::Value;
use std::io::Write;
use std::path::Path;

const TIMEOUT_SECS: u64 = 30;
const REDACTED: &str = "REDACTED";

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

#[derive(Debug, Clone)]
pub struct OpsmlApiClient {
    pub client: Client,
    settings: OpsmlStorageSettings,
    base_path: String,
}

impl OpsmlApiClient {
    pub async fn new(settings: &OpsmlStorageSettings, client: &Client) -> Result<Self, ApiError> {
        // setup headers

        let mut api_client = Self {
            client: client.clone(),
            settings: settings.clone(),
            base_path: format!(
                "{}/{}",
                settings.api_settings.base_url, settings.api_settings.opsml_dir
            ),
        };

        if settings.api_settings.use_auth {
            api_client.get_jwt_token().await?;

            // mask the username and password
            api_client.settings.api_settings.username = REDACTED.to_string();
            api_client.settings.api_settings.password = REDACTED.to_string();

            // mask the env variables
            std::env::set_var("OPSML_USERNAME", REDACTED);
            std::env::set_var("OPSML_PASSWORD", REDACTED);
        }

        Ok(api_client)
    }

    async fn get_jwt_token(&mut self) -> Result<(), ApiError> {
        if !self.settings.api_settings.use_auth {
            return Ok(());
        }

        let mut headers = HeaderMap::new();
        headers.insert(
            "Username",
            HeaderValue::from_str(&self.settings.api_settings.username).map_err(|e| {
                ApiError::Error(format!("Failed to create header with error: {}", e))
            })?,
        );

        headers.insert(
            "Password",
            HeaderValue::from_str(&self.settings.api_settings.password).map_err(|e| {
                ApiError::Error(format!("Failed to create header with error: {}", e))
            })?,
        );

        let url = format!("{}/{}", self.base_path, Routes::AuthApiLogin.as_str());
        let response = self
            .client
            .get(url)
            .headers(headers)
            .send()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to send request with error: {}", e)))?
            .json::<JwtToken>()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to parse response with error: {}", e)))?;

        self.settings.api_settings.auth_token = response.token;

        Ok(())
    }

    /// Refresh the JWT token when it expires
    /// This function is called with the old JWT token, which is then verified with the server refresh token
    async fn refresh_token(&mut self) -> Result<(), ApiError> {
        if !self.settings.api_settings.use_auth {
            return Ok(());
        }

        let url = format!("{}/{}", self.base_path, Routes::AuthApiRefresh.as_str());
        let response = self
            .client
            .get(url)
            .bearer_auth(&self.settings.api_settings.auth_token)
            .send()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to send request with error: {}", e)))?
            .json::<JwtToken>()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to parse response with error: {}", e)))?;

        self.settings.api_settings.auth_token = response.token;

        Ok(())
    }

    async fn request(
        self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_string: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<Response, ApiError> {
        let headers = headers.unwrap_or_default();

        let url = format!("{}/{}", self.base_path, route.as_str());
        let response = match request_type {
            RequestType::Get => {
                let url = if let Some(query_string) = query_string {
                    format!("{}?{}", url, query_string)
                } else {
                    url
                };

                self.client
                    .get(url)
                    .headers(headers)
                    .bearer_auth(&self.settings.api_settings.auth_token)
                    .send()
                    .await
                    .map_err(|e| {
                        ApiError::Error(format!("Failed to send request with error: {}", e))
                    })?
            }
            RequestType::Post => self
                .client
                .post(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.settings.api_settings.auth_token)
                .send()
                .await
                .map_err(|e| {
                    ApiError::Error(format!("Failed to send request with error: {}", e))
                })?,
            RequestType::Put => self
                .client
                .put(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.settings.api_settings.auth_token)
                .send()
                .await
                .map_err(|e| {
                    ApiError::Error(format!("Failed to send request with error: {}", e))
                })?,
            RequestType::Delete => {
                let url = if let Some(query_string) = query_string {
                    format!("{}?{}", url, query_string)
                } else {
                    url
                };
                self.client
                    .delete(url)
                    .headers(headers)
                    .bearer_auth(self.settings.api_settings.auth_token)
                    .send()
                    .await
                    .map_err(|e| {
                        ApiError::Error(format!("Failed to send request with error: {}", e))
                    })?
            }
        };

        Ok(response)
    }

    pub async fn request_with_retry(
        &mut self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<Response, ApiError> {
        // this will attempt to send a request. If the request fails, it will refresh the token and try again. If it fails all 3 times it will return an error
        let mut attempts = 0;
        let max_attempts = 3;
        let mut response: Result<Response, ApiError>;

        loop {
            attempts += 1;

            let client = self.clone();
            response = client
                .request(
                    route.clone(),
                    request_type.clone(),
                    body_params.clone(),
                    query_params.clone(),
                    headers.clone(),
                )
                .await;

            if response.is_ok() || attempts >= max_attempts {
                break;
            }

            if response.is_err() {
                self.refresh_token().await.map_err(|e| {
                    ApiError::Error(format!("Failed to refresh token with error: {}", e))
                })?;
            }
        }

        let response = response
            .map_err(|e| ApiError::Error(format!("Failed to send request with error: {}", e)))?;

        Ok(response)
    }

    // specific method for multipart uploads (mainly used for localstorageclient)
    pub async fn multipart_upload(self, form: Form) -> Result<Response, ApiError> {
        let response = self
            .client
            .post(format!("{}/files/multipart", self.base_path))
            .multipart(form)
            .bearer_auth(self.settings.api_settings.auth_token)
            .send()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to send request with error: {}", e)))?;
        Ok(response)
    }

    // specific method for multipart uploads (mainly used for localstorageclient)
    pub async fn generate_presigned_url_for_part(
        &mut self,
        path: &str,
        session_url: &str,
        part_number: i32,
    ) -> Result<String, ApiError> {
        let args = PresignedQuery {
            path: path.to_string(),
            session_url: Some(session_url.to_string()),
            part_number: Some(part_number),
            for_multi_part: Some(true),
        };
        let query_string = serde_qs::to_string(&args).map_err(|e| {
            ApiError::Error(format!(
                "Failed to serialize query string with error: {}",
                e
            ))
        })?;

        let response = self
            .request_with_retry(
                Routes::Presigned,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .map_err(|e| ApiError::Error(format!("Failed to generate presigned url: {}", e)))?;

        // move response into PresignedUrl
        let response = response
            .json::<Value>()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to parse response with error: {}", e)))?;

        let response = serde_json::from_value::<PresignedUrl>(response)
            .map_err(|e| ApiError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(response.url)
    }
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
    async fn get_storage_setting(client: &mut OpsmlApiClient) -> Result<StorageType, StorageError> {
        let response = client
            .request_with_retry(Routes::StorageSettings, RequestType::Get, None, None, None)
            .await
            .map_err(|e| {
                let error = Colorize::alert(&format!("Failed to get storage settings: {}", e));
                StorageError::Error(error)
            })?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        // convert Value to Vec<String>
        let settings = serde_json::from_value::<StorageSettings>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(settings.storage_type)
    }

    pub async fn find(&mut self, path: &str) -> Result<Vec<String>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)
            .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

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
            .map_err(|e| StorageError::Error(format!("Failed to get files: {}", e)))?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        // convert Value to Vec<String>
        let response = serde_json::from_value::<ListFileResponse>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(response.files)
    }

    pub async fn find_info(&mut self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let query = ListFileQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)
            .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

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
            .map_err(|e| StorageError::Error(format!("Failed to get files: {}", e)))?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        let response = serde_json::from_value::<ListFileInfoResponse>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

        Ok(response.files)
    }

    pub async fn get_object(
        &mut self,
        local_path: &str,
        remote_path: &str,
        file_size: i64,
    ) -> Result<(), StorageError> {
        // check if local path exists, create it if it doesn't
        let local_path = Path::new(local_path);

        if !local_path.exists() {
            std::fs::create_dir_all(local_path.parent().unwrap())
                .map_err(|e| StorageError::Error(format!("Failed to create directory: {}", e)))?;
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
        let mut file = std::fs::File::create(local_path)
            .map_err(|e| StorageError::Error(format!("Failed to create file: {}", e)))?;

        // generate presigned url for downloading the object
        let presigned_url = self.generate_presigned_url(remote_path).await?;

        // download the object
        let mut response = if self.storage_type == StorageType::Local {
            let query = DownloadFileQuery {
                path: remote_path.to_string(),
            };

            let query_string = serde_qs::to_string(&query)
                .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

            self.api_client
                .request_with_retry(
                    Routes::Files,
                    RequestType::Get,
                    None,
                    Some(query_string),
                    None,
                )
                .await
                .map_err(|e| StorageError::Error(format!("Failed to get file: {}", e)))?
        } else {
            // if storage clients are gcs, aws and azure, use presigned url to download the object
            // If local storage client, download the object from api route
            let url = reqwest::Url::parse(&presigned_url)
                .map_err(|e| StorageError::Error(format!("Invalid presigned URL: {}", e)))?;

            self.api_client.client.get(url).send().await.unwrap()
        };

        // create buffer to store downloaded data
        let mut buffer = BytesMut::with_capacity(DOWNLOAD_CHUNK_SIZE);

        // download the object in chunks
        while let Some(chunk) = response
            .chunk()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to get chunk from response: {}", e)))?
        {
            buffer.extend_from_slice(&chunk);
            if buffer.len() >= DOWNLOAD_CHUNK_SIZE {
                file.write_all(&buffer)
                    .map_err(|e| StorageError::Error(format!("Failed to write chunk: {}", e)))?;
                buffer.clear();
                bar.inc(1);
            }
        }

        // Write any remaining data in the buffer
        if !buffer.is_empty() {
            file.write_all(&buffer).map_err(|e| {
                StorageError::Error(format!("Failed to write remaining data: {}", e))
            })?;
        }

        bar.finish_with_message("Download complete");
        Ok(())
    }

    pub async fn delete_object(&mut self, path: &str) -> Result<bool, StorageError> {
        let query = DeleteFileQuery {
            path: path.to_string(),
            recursive: false,
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

        // load DeleteFileResponse from response
        let response = serde_json::from_value::<DeleteFileResponse>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

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

    pub async fn create_multipart_upload(&mut self, path: &str) -> Result<String, StorageError> {
        let query = MultiPartQuery {
            path: path.to_string(),
        };

        let query_string = serde_qs::to_string(&query)
            .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

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
                StorageError::Error(format!("Failed to create multipart upload: {}", e))
            })?;

        // deserialize response into MultiPartSession
        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        let session = serde_json::from_value::<MultiPartSession>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

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

    pub async fn generate_presigned_url(&mut self, path: &str) -> Result<String, StorageError> {
        let query = PresignedQuery {
            path: path.to_string(),
            ..Default::default()
        };

        let query_string = serde_qs::to_string(&query)
            .map_err(|e| StorageError::Error(format!("Failed to serialize query: {}", e)))?;

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
            .map_err(|e| StorageError::Error(format!("Failed to generate presigned url: {}", e)))?;

        let val = response
            .json::<Value>()
            .await
            .map_err(|e| StorageError::Error(format!("Failed to parse response: {}", e)))?;

        let response = serde_json::from_value::<PresignedUrl>(val)
            .map_err(|e| StorageError::Error(format!("Failed to deserialize response: {}", e)))?;

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
