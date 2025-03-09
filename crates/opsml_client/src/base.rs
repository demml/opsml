use crate::types::{JwtToken, RequestType, Routes};
use opsml_error::error::ApiError;
use opsml_settings::config::{ApiSettings, OpsmlStorageSettings};
use opsml_types::contracts::{PresignedQuery, PresignedUrl};

use reqwest::header;
use reqwest::multipart::Form;
use reqwest::Response;
use reqwest::{
    header::{HeaderMap, HeaderValue},
    Client,
};
use serde_json::Value;
use tracing::{debug, error, instrument};

const TIMEOUT_SECS: u64 = 30;

/// Create a new HTTP client that can be shared across different clients
#[instrument(skip_all)]
pub fn build_http_client(settings: &ApiSettings) -> Result<Client, ApiError> {
    let mut headers = HeaderMap::new();

    headers.insert(
        "X-Prod-Token",
        HeaderValue::from_str(settings.prod_token.as_deref().unwrap_or(""))
            .map_err(|e| ApiError::Error(format!("Failed to create header with error: {}", e)))?,
    );

    headers.insert(
        "Username",
        HeaderValue::from_str(&settings.username)
            .map_err(|e| ApiError::Error(format!("Failed to create header with error: {}", e)))?,
    );

    headers.insert(
        "Password",
        HeaderValue::from_str(&settings.password)
            .map_err(|e| ApiError::Error(format!("Failed to create header with error: {}", e)))?,
    );

    debug!("Creating client with headers: {:?}", headers);

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

        api_client.get_jwt_token().await.map_err(|e| {
            error!("Failed to get JWT token: {}", e);
            ApiError::Error(format!("Failed to get JWT token with error: {}", e))
        })?;

        Ok(api_client)
    }

    #[instrument(skip_all)]
    async fn get_jwt_token(&mut self) -> Result<(), ApiError> {
        let url = format!("{}/{}", self.base_path, Routes::AuthLogin.as_str());
        debug!("Getting JWT token from {}", url);

        let response =
            self.client.get(url).send().await.map_err(|e| {
                ApiError::Error(format!("Failed to send request with error: {}", e))
            })?;

        // check if unauthorized
        if response.status().is_client_error() {
            error!("Failed to get JWT token: Unauthorized");
            return Err(ApiError::Error("Unauthorized".to_string()));
        }

        let response = response
            .json::<JwtToken>()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to parse response with error: {}", e)))?;

        self.settings.api_settings.auth_token = response.token;

        Ok(())
    }

    async fn update_token_from_response(&mut self, response: &Response) {
        if let Some(new_token) = response
            .headers()
            .get(header::AUTHORIZATION)
            .and_then(|h| h.to_str().ok())
            .and_then(|h| h.strip_prefix("Bearer "))
        {
            self.settings.api_settings.auth_token = new_token.to_string();
        }
    }

    async fn _request(
        &self,
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
                .bearer_auth(&self.settings.api_settings.auth_token)
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
                .bearer_auth(&self.settings.api_settings.auth_token)
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
                    .bearer_auth(&self.settings.api_settings.auth_token)
                    .send()
                    .await
                    .map_err(|e| {
                        ApiError::Error(format!("Failed to send request with error: {}", e))
                    })?
            }
        };

        Ok(response)
    }

    pub async fn request(
        &mut self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
    ) -> Result<Response, ApiError> {
        let response = self
            ._request(
                route.clone(),
                request_type,
                body_params,
                query_params,
                headers,
            )
            .await?;

        // Check and update token if a new one was provided
        self.update_token_from_response(&response).await;

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
            .request(
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

    async fn setup_client(server_url: String) -> OpsmlApiClient {
        let config = OpsmlConfig::new(None);
        let mut settings = config.storage_settings().unwrap();

        // set up some auth
        settings.api_settings.username = "username".to_string();
        settings.api_settings.password = "password".to_string();
        settings.api_settings.base_url = server_url.to_string();

        let client = build_http_client(&settings.api_settings).unwrap();
        OpsmlApiClient::new(&settings, &client).await.unwrap()
    }

    #[tokio::test]
    async fn test_api_client_no_auth() {
        let (mut server, server_url) = setup_server().await;
        let mut api_client = setup_client(server_url).await;

        let _mock = server
            .mock("GET", "/opsml/files")
            .with_status(200)
            .with_body(r#"{"status": "ok"}"#)
            .create();

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
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

        let mut api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .await
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

        let mut api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .await
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

        let mut api_client = setup_client(server_url).await;
        let result = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .await;

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

        let mut api_client = setup_client(server_url).await;

        let response = api_client
            .request(Routes::Files, RequestType::Get, None, None, None)
            .await
            .unwrap();

        assert_eq!(response.status(), 200);

        _first_attempt_mock.assert();
        _second_attempt_mock.assert();
        _initial_token_mock.assert();
        _refresh_token_mock.assert();
    }
}
