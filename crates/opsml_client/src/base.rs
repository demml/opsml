use crate::error::ApiClientError;
use opsml_settings::config::{ApiSettings, OpsmlStorageSettings};
use opsml_types::{
    api::{JwtToken, RequestType, Routes},
    contracts::{CompleteMultipartUpload, PresignedQuery, PresignedUrl},
};

use reqwest::blocking::{Client, Response, multipart::Form};
use reqwest::header::{AUTHORIZATION, HeaderMap, HeaderValue};
use reqwest::{Client as AsyncClient, Response as AsyncResponse, multipart::Form as AsyncForm};
use serde_json::Value;
use std::sync::Arc;
use std::sync::RwLock;
use std::thread;
use std::time::Duration;
use tracing::{debug, error, instrument};
const MAX_RETRIES: u32 = 3;
const INITIAL_BACKOFF_MS: u64 = 100;
const MAX_BACKOFF_MS: u64 = 5000;
const TIMEOUT_SECS: u64 = 30;

/// Create a new HTTP client that can be shared across different clients
pub fn build_http_client(settings: &ApiSettings) -> Result<Client, ApiClientError> {
    let mut headers = HeaderMap::new();

    headers.insert(
        "X-Prod-Token",
        HeaderValue::from_str(settings.prod_token.as_deref().unwrap_or(""))
            .map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Username",
        HeaderValue::from_str(&settings.username).map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Password",
        HeaderValue::from_str(&settings.password).map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Use-SSO",
        HeaderValue::from_str(&settings.use_sso.to_string())
            .map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        reqwest::header::USER_AGENT,
        HeaderValue::from_static("opsml-client/"),
    );
    let client_builder = Client::builder().timeout(std::time::Duration::from_secs(TIMEOUT_SECS));

    let client = client_builder
        .default_headers(headers)
        .build()
        .map_err(ApiClientError::CreateClientError)?;

    Ok(client)
}

pub fn build_async_http_client(settings: &ApiSettings) -> Result<AsyncClient, ApiClientError> {
    let mut headers = HeaderMap::new();

    headers.insert(
        "X-Prod-Token",
        HeaderValue::from_str(settings.prod_token.as_deref().unwrap_or(""))
            .map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Username",
        HeaderValue::from_str(&settings.username).map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Password",
        HeaderValue::from_str(&settings.password).map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        "Use-SSO",
        HeaderValue::from_str(&settings.use_sso.to_string())
            .map_err(ApiClientError::CreateHeaderError)?,
    );

    headers.insert(
        reqwest::header::USER_AGENT,
        HeaderValue::from_static("opsml-client/"),
    );
    let client_builder =
        AsyncClient::builder().timeout(std::time::Duration::from_secs(TIMEOUT_SECS));

    let client = client_builder
        .default_headers(headers)
        .build()
        .map_err(ApiClientError::CreateClientError)?;

    Ok(client)
}

/// Main client for interacting with the OpsML API
/// This client acquires a JWT token on creation, which is stored in a RwLock
/// and used for all subsequent requests. All token refreshes are handled on the server side.
/// That is, if a request fails auth during a request, the server will complete the request
/// and return a new token if the server refresh token is still valid
///
///  Arguments:
///
/// - `client`: reqwest client to use for requests
/// - `url`: base url for the API
///
#[derive(Debug, Clone)]
pub struct OpsmlApiClient {
    pub client: Client,
    base_path: String,
    auth_token: Arc<RwLock<String>>,
}

impl OpsmlApiClient {
    pub fn new(url: String, client: &Client) -> Result<Self, ApiClientError> {
        // setup headers
        let api_client = Self {
            client: client.clone(),
            base_path: url,
            auth_token: Arc::new(RwLock::new(String::new())),
        };

        api_client.refresh_token().inspect_err(|e| {
            error!("Failed to get JWT token: {e}");
        })?;

        Ok(api_client)
    }

    #[instrument(skip_all)]
    fn refresh_token(&self) -> Result<(), ApiClientError> {
        let url = format!("{}/{}", self.base_path, Routes::AuthLogin.as_str());
        debug!("Getting JWT token from {}", url);

        let response = self
            .client
            .get(url)
            .send()
            .map_err(ApiClientError::RequestError)?;

        // check if unauthorized
        if response.status().is_client_error() {
            return Err(ApiClientError::Unauthorized);
        }

        let token = response
            .json::<JwtToken>()
            .map_err(ApiClientError::RequestError)?;

        if let Ok(mut token_guard) = self.auth_token.write() {
            *token_guard = token.token;
        } else {
            error!("Failed to acquire write lock for token update");
            return Err(ApiClientError::UpdateAuthError);
        }

        Ok(())
    }

    fn update_token_from_response(&self, response: &Response) {
        if let Some(new_token) = response
            .headers()
            .get(AUTHORIZATION)
            .and_then(|h| h.to_str().ok())
            .and_then(|h| h.strip_prefix("Bearer "))
        {
            match self.auth_token.write() {
                Ok(mut token_guard) => {
                    *token_guard = new_token.to_string();
                }
                Err(e) => {
                    error!("Failed to acquire write lock for jwt token update: {e}");
                }
            }
        }
    }

    fn get_current_token(&self) -> String {
        match self.auth_token.read() {
            Ok(token_guard) => token_guard.clone(),
            Err(e) => {
                error!("Failed to acquire read lock for token: {e}");
                "".to_string()
            }
        }
    }

    fn _request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_string: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<Response, ApiClientError> {
        let headers = headers.unwrap_or_default();

        let url = format!("{}/{}", self.base_path, route.as_str());
        let response = match request_type {
            RequestType::Get => {
                let url = if let Some(query_string) = query_string {
                    format!("{url}?{query_string}")
                } else {
                    url
                };

                self.client
                    .get(url)
                    .headers(headers)
                    .bearer_auth(self.get_current_token())
                    .send()
                    .map_err(ApiClientError::RequestError)?
            }
            RequestType::Post => self
                .client
                .post(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.get_current_token())
                .send()
                .map_err(ApiClientError::RequestError)?,
            RequestType::Put => self
                .client
                .put(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.get_current_token())
                .send()
                .map_err(ApiClientError::RequestError)?,
            RequestType::Delete => {
                let url = if let Some(query_string) = query_string {
                    format!("{url}?{query_string}")
                } else {
                    url
                };
                self.client
                    .delete(url)
                    .headers(headers)
                    .bearer_auth(self.get_current_token())
                    .send()
                    .map_err(ApiClientError::RequestError)?
            }
        };

        Ok(response)
    }

    pub fn request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<Response, ApiClientError> {
        self.request_with_retry(
            route,
            request_type,
            body_params,
            query_params,
            headers,
            MAX_RETRIES,
        )
    }

    fn request_with_retry(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
        max_retries: u32,
    ) -> Result<Response, ApiClientError> {
        let mut attempt = 0;
        let mut backoff_ms = INITIAL_BACKOFF_MS;

        loop {
            match self._request(
                route.clone(),
                request_type.clone(),
                body_params.clone(),
                query_params.clone(),
                headers.clone(),
            ) {
                Ok(response) => {
                    // handle if response is an error status code
                    if Self::is_retryable_status(response.status()) && attempt < max_retries {
                        debug!(
                            "Request failed with retryable status {}, attempt {}/{}",
                            response.status(),
                            attempt + 1,
                            max_retries
                        );
                        attempt += 1;
                        thread::sleep(Duration::from_millis(backoff_ms));
                        backoff_ms = (backoff_ms * 2).min(MAX_BACKOFF_MS);
                        continue;
                    }

                    self.update_token_from_response(&response);
                    return Ok(response);
                }
                Err(e) => {
                    // handle client error
                    if Self::is_retryable_error(&e) && attempt < max_retries {
                        debug!(
                            "Request failed with retryable error: {}, attempt {}/{}",
                            e,
                            attempt + 1,
                            max_retries
                        );
                        attempt += 1;
                        thread::sleep(Duration::from_millis(backoff_ms));
                        backoff_ms = (backoff_ms * 2).min(MAX_BACKOFF_MS);
                        continue;
                    }
                    return Err(e);
                }
            }
        }
    }

    fn is_retryable_status(status: reqwest::StatusCode) -> bool {
        matches!(
            status.as_u16(),
            408 | // Request Timeout
            429 | // Too Many Requests
            500 | // Internal Server Error
            502 | // Bad Gateway
            503 | // Service Unavailable
            504 // Gateway Timeout
        )
    }

    fn is_retryable_error(error: &ApiClientError) -> bool {
        matches!(
            error,
            ApiClientError::RequestError(e) if e.is_timeout() || e.is_connect()
        )
    }

    // specific method for multipart uploads (mainly used for localstorageclient)
    pub fn multipart_upload(&self, form: Form) -> Result<Response, ApiClientError> {
        let response = self
            .client
            .post(format!("{}/files/multipart", self.base_path))
            .multipart(form)
            .bearer_auth(self.get_current_token())
            .send()
            .map_err(ApiClientError::RequestError)?;
        Ok(response)
    }

    // specific method for multipart uploads (mainly used for aws)
    pub fn generate_presigned_url_for_part(
        &self,
        path: &str,
        session_url: &str,
        part_number: i32,
    ) -> Result<String, ApiClientError> {
        let args = PresignedQuery {
            path: path.to_string(),
            session_url: Some(session_url.to_string()),
            part_number: Some(part_number),
            for_multi_part: Some(true),
        };
        let query_string = serde_qs::to_string(&args)?;

        let response = self
            .request(
                Routes::Presigned,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .inspect_err(|e| {
                error!("Failed to get presigned url with error: {e}");
            })?;

        // move response into PresignedUrl
        let response = response.json::<PresignedUrl>()?;

        Ok(response.url)
    }

    // specific method for completing multipart uploads (used for aws)
    pub fn complete_multipart_upload(
        &self,
        complete_request: CompleteMultipartUpload,
    ) -> Result<Response, ApiClientError> {
        let body = serde_json::to_value(complete_request).inspect_err(|e| {
            error!(
                "Failed to serialize completed upload parts with error: {}",
                e
            );
        })?;

        let url = format!("{}/{}", self.base_path, Routes::CompleteMultipart);
        let response = self
            .client
            .post(url)
            .json(&body)
            .bearer_auth(self.get_current_token())
            .send()
            .map_err(ApiClientError::RequestError)?;
        Ok(response)
    }
}

/// Async version of OpsmlApiClient
///
///  Arguments:
///
/// - `client`: reqwest client to use for requests
/// - `url`: base url for the API
///
#[derive(Debug, Clone)]
pub struct OpsmlApiAsyncClient {
    pub client: AsyncClient,
    base_path: String,
    auth_token: Arc<RwLock<String>>,
}

impl OpsmlApiAsyncClient {
    pub async fn new(url: String, client: &AsyncClient) -> Result<Self, ApiClientError> {
        // setup headers
        let api_client = Self {
            client: client.clone(),
            base_path: url,
            auth_token: Arc::new(RwLock::new(String::new())),
        };

        api_client.refresh_token().await.inspect_err(|e| {
            error!("Failed to get JWT token: {e}");
        })?;

        Ok(api_client)
    }

    #[instrument(skip_all)]
    async fn refresh_token(&self) -> Result<(), ApiClientError> {
        let url = format!("{}/{}", self.base_path, Routes::AuthLogin.as_str());
        debug!("Getting JWT token from {}", url);

        let response = self
            .client
            .get(url)
            .send()
            .await
            .map_err(ApiClientError::RequestError)?;

        // check if unauthorized
        if response.status().is_client_error() {
            return Err(ApiClientError::Unauthorized);
        }

        let token = response
            .json::<JwtToken>()
            .await
            .map_err(ApiClientError::RequestError)?;

        if let Ok(mut token_guard) = self.auth_token.write() {
            *token_guard = token.token;
        } else {
            error!("Failed to acquire write lock for token update");
            return Err(ApiClientError::UpdateAuthError);
        }

        Ok(())
    }

    fn update_token_from_response(&self, response: &AsyncResponse) {
        if let Some(new_token) = response
            .headers()
            .get(AUTHORIZATION)
            .and_then(|h| h.to_str().ok())
            .and_then(|h| h.strip_prefix("Bearer "))
        {
            match self.auth_token.write() {
                Ok(mut token_guard) => {
                    *token_guard = new_token.to_string();
                }
                Err(e) => {
                    error!("Failed to acquire write lock for jwt token update: {e}");
                }
            }
        }
    }

    fn get_current_token(&self) -> String {
        match self.auth_token.read() {
            Ok(token_guard) => token_guard.clone(),
            Err(e) => {
                error!("Failed to acquire read lock for token: {e}");
                "".to_string()
            }
        }
    }

    async fn _request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_string: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<AsyncResponse, ApiClientError> {
        let headers = headers.unwrap_or_default();

        let url = format!("{}/{}", self.base_path, route.as_str());
        let response = match request_type {
            RequestType::Get => {
                let url = if let Some(query_string) = query_string {
                    format!("{url}?{query_string}")
                } else {
                    url
                };

                self.client
                    .get(url)
                    .headers(headers)
                    .bearer_auth(self.get_current_token())
                    .send()
                    .await
                    .map_err(ApiClientError::RequestError)?
            }
            RequestType::Post => self
                .client
                .post(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.get_current_token())
                .send()
                .await
                .map_err(ApiClientError::RequestError)?,
            RequestType::Put => self
                .client
                .put(url)
                .headers(headers)
                .json(&body_params)
                .bearer_auth(self.get_current_token())
                .send()
                .await
                .map_err(ApiClientError::RequestError)?,
            RequestType::Delete => {
                let url = if let Some(query_string) = query_string {
                    format!("{url}?{query_string}")
                } else {
                    url
                };
                self.client
                    .delete(url)
                    .headers(headers)
                    .bearer_auth(self.get_current_token())
                    .send()
                    .await
                    .map_err(ApiClientError::RequestError)?
            }
        };

        Ok(response)
    }

    pub async fn request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<AsyncResponse, ApiClientError> {
        self.request_with_retry(
            route,
            request_type,
            body_params,
            query_params,
            headers,
            MAX_RETRIES,
        )
        .await
    }

    async fn request_with_retry(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
        max_retries: u32,
    ) -> Result<AsyncResponse, ApiClientError> {
        let mut attempt = 0;
        let mut backoff_ms = INITIAL_BACKOFF_MS;

        loop {
            match self
                ._request(
                    route.clone(),
                    request_type.clone(),
                    body_params.clone(),
                    query_params.clone(),
                    headers.clone(),
                )
                .await
            {
                Ok(response) => {
                    if Self::is_retryable_status(response.status()) && attempt < max_retries {
                        debug!(
                            "Request failed with retryable status {}, attempt {}/{}",
                            response.status(),
                            attempt + 1,
                            max_retries
                        );
                        attempt += 1;
                        tokio::time::sleep(Duration::from_millis(backoff_ms)).await;
                        backoff_ms = (backoff_ms * 2).min(MAX_BACKOFF_MS);
                        continue;
                    }

                    self.update_token_from_response(&response);
                    return Ok(response);
                }
                Err(e) => {
                    if Self::is_retryable_error(&e) && attempt < max_retries {
                        debug!(
                            "Request failed with retryable error: {}, attempt {}/{}",
                            e,
                            attempt + 1,
                            max_retries
                        );
                        attempt += 1;
                        tokio::time::sleep(Duration::from_millis(backoff_ms)).await;
                        backoff_ms = (backoff_ms * 2).min(MAX_BACKOFF_MS);
                        continue;
                    }
                    return Err(e);
                }
            }
        }
    }

    fn is_retryable_status(status: reqwest::StatusCode) -> bool {
        matches!(status.as_u16(), 408 | 429 | 500 | 502 | 503 | 504)
    }

    fn is_retryable_error(error: &ApiClientError) -> bool {
        matches!(
            error,
            ApiClientError::RequestError(e) if e.is_timeout() || e.is_connect()
        )
    }

    // specific method for multipart uploads (mainly used for localstorageclient)
    pub async fn multipart_upload(&self, form: AsyncForm) -> Result<AsyncResponse, ApiClientError> {
        let response = self
            .client
            .post(format!("{}/files/multipart", self.base_path))
            .multipart(form)
            .bearer_auth(self.get_current_token())
            .send()
            .await
            .map_err(ApiClientError::RequestError)?;
        Ok(response)
    }

    // specific method for multipart uploads (mainly used for aws)
    pub async fn generate_presigned_url_for_part(
        &self,
        path: &str,
        session_url: &str,
        part_number: i32,
    ) -> Result<String, ApiClientError> {
        let args = PresignedQuery {
            path: path.to_string(),
            session_url: Some(session_url.to_string()),
            part_number: Some(part_number),
            for_multi_part: Some(true),
        };
        let query_string = serde_qs::to_string(&args)?;

        let response = self
            .request(
                Routes::Presigned,
                RequestType::Get,
                None,
                Some(query_string),
                None,
            )
            .await
            .inspect_err(|e| {
                error!("Failed to get presigned url with error: {e}");
            })?;

        // move response into PresignedUrl
        let response = response.json::<PresignedUrl>().await?;

        Ok(response.url)
    }

    // specific method for completing multipart uploads (used for aws)
    pub async fn complete_multipart_upload(
        &self,
        complete_request: CompleteMultipartUpload,
    ) -> Result<AsyncResponse, ApiClientError> {
        let body = serde_json::to_value(complete_request).inspect_err(|e| {
            error!(
                "Failed to serialize completed upload parts with error: {}",
                e
            );
        })?;

        let url = format!("{}/{}", self.base_path, Routes::CompleteMultipart);
        let response = self
            .client
            .post(url)
            .json(&body)
            .bearer_auth(self.get_current_token())
            .send()
            .await
            .map_err(|e| {
                error!("Failed to complete multipart upload with error: {}", e);
                ApiClientError::RequestError(e)
            })?;
        Ok(response)
    }
}

pub fn build_api_client(settings: &OpsmlStorageSettings) -> Result<OpsmlApiClient, ApiClientError> {
    let client = build_http_client(&settings.api_settings)?;

    let url = format!(
        "{}/{}",
        settings.api_settings.base_url, settings.api_settings.opsml_dir
    );
    OpsmlApiClient::new(url, &client)
}

pub async fn build_async_api_client(
    settings: &OpsmlStorageSettings,
) -> Result<OpsmlApiAsyncClient, ApiClientError> {
    let client = build_async_http_client(&settings.api_settings)?;

    let url = format!(
        "{}/{}",
        settings.api_settings.base_url, settings.api_settings.opsml_dir
    );
    OpsmlApiAsyncClient::new(url, &client).await
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

    async fn setup_client(server_url: String) -> OpsmlApiClient {
        let config = OpsmlConfig::new();
        let mut settings = config.storage_settings().unwrap();

        // set up some auth
        settings.api_settings.username = "username".to_string();
        settings.api_settings.password = "password".to_string();
        settings.api_settings.base_url = server_url.to_string();

        let client = build_http_client(&settings.api_settings).unwrap();
        let url = format!("{}/{}", server_url, settings.api_settings.opsml_dir);
        OpsmlApiClient::new(url, &client).unwrap()
    }

    #[tokio::test]
    async fn test_api_client_no_auth() {
        let (mut server, server_url) = setup_server().await;
        let api_client = setup_client(server_url).await;

        let _mock = server
            .mock("GET", "/opsml/files")
            .with_status(200)
            .with_body(r#"{"status": "ok"}"#)
            .create();

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
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

        let api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .unwrap();

        assert_eq!(response.status(), 200);
    }

    #[tokio::test]
    async fn test_request_success() {
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

        let api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .unwrap();

        assert_eq!(response.status(), 200);
    }

    #[tokio::test]
    async fn test_request_failure() {
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

        let api_client = setup_client(server_url).await;
        let result = api_client.request(Routes::Files, RequestType::Get, None, None, None);

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_request_auth_refresh() {
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

        let api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .unwrap();

        assert_eq!(response.status(), 200);

        _first_attempt_mock.assert();
        _second_attempt_mock.assert();
        _initial_token_mock.assert();
        _refresh_token_mock.assert();
    }
}
