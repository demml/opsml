use crate::types::{JwtToken, RequestType, Routes};
use opsml_error::error::ApiError;
use opsml_settings::config::{ApiSettings, OpsmlStorageSettings};
use opsml_types::contracts::{PresignedQuery, PresignedUrl};

use reqwest::multipart::Form;
use reqwest::Response;
use reqwest::{
    header::{HeaderMap, HeaderValue},
    Client,
};
use serde_json::Value;

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
    header_map: HeaderMap,
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
            header_map: OpsmlApiClient::get_default_headers(&settings.api_settings).await?,
        };

        if settings.api_settings.use_auth {
            api_client.get_jwt_token().await?;

            // mask the password
            api_client.settings.api_settings.password = REDACTED.to_string();

            // mask the env variables
            std::env::set_var("OPSML_PASSWORD", REDACTED);
        }

        Ok(api_client)
    }

    async fn get_default_headers(api_settings: &ApiSettings) -> Result<HeaderMap, ApiError> {
        let mut headers = HeaderMap::new();

        headers.insert(
            "Username",
            HeaderValue::from_str(&api_settings.username).map_err(|e| {
                ApiError::Error(format!("Failed to create header with error: {}", e))
            })?,
        );

        headers.insert(
            "Password",
            HeaderValue::from_str(&api_settings.password).map_err(|e| {
                ApiError::Error(format!("Failed to create header with error: {}", e))
            })?,
        );

        headers.insert(
            "X-Prod-Token",
            HeaderValue::from_str(&api_settings.prod_token.as_deref().unwrap_or("")).unwrap(),
        );

        Ok(headers)
    }

    async fn get_jwt_token(&mut self) -> Result<(), ApiError> {
        if !self.settings.api_settings.use_auth {
            return Ok(());
        }

        let url = format!("{}/{}", self.base_path, Routes::AuthApiLogin.as_str());
        let response = self
            .client
            .get(url)
            .headers(self.header_map.clone())
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
        let provided_headers = headers.unwrap_or_default();
        let mut headers = self.header_map.clone();

        // insert headers into the header map
        for (key, value) in provided_headers.iter() {
            headers.insert(key, value.clone());
        }

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
        let mut settings = config.storage_settings().unwrap();

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
