use anyhow::Result;
use opsml_client::{RequestType, Routes};

use opsml_error::{ApiError, ServerError};
use opsml_settings::config::ScouterSettings;

/// Route for debugging information
use reqwest::Response;
use reqwest::{header::HeaderMap, Client};
use serde_json::Value;

const TIMEOUT_SECS: u64 = 30;
pub async fn build_scouter_http_client(settings: &ScouterSettings) -> Result<ScouterApiClient> {
    let client_builder = Client::builder().timeout(std::time::Duration::from_secs(TIMEOUT_SECS));
    let client = client_builder
        .build()
        .map_err(|e| ServerError::Error(format!("Failed to create client with error: {}", e)))?;

    let base_path = settings.server_uri.clone();

    let enabled = !base_path.is_empty();

    Ok(ScouterApiClient {
        client,
        base_path,
        enabled,
    })
}

#[derive(Debug, Clone)]
pub struct ScouterApiClient {
    pub client: Client,
    pub base_path: String,
    pub enabled: bool,
}

impl ScouterApiClient {
    async fn _request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_string: Option<String>,
        headers: Option<HeaderMap>,
        bearer_token: String,
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
                    .bearer_auth(&bearer_token)
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
                .bearer_auth(&bearer_token)
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
                .bearer_auth(&bearer_token)
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
                    .bearer_auth(&bearer_token)
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
        bearer_token: String,
    ) -> Result<Response, ApiError> {
        let response = self
            ._request(
                route.clone(),
                request_type,
                body_params,
                query_params,
                headers,
                bearer_token,
            )
            .await?;

        Ok(response)
    }
}
