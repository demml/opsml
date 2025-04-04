use anyhow::Result;
use opsml_client::RequestType;

use opsml_error::{ApiError, ServerError};
use opsml_settings::config::ScouterSettings;

use opsml_sql::schemas::User;
/// Route for debugging information
use reqwest::Response;
use reqwest::{header::HeaderMap, Client};
use serde_json::Value;

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum Routes {
    DriftCustom,
    DriftPsi,
    DriftSpc,
    Profile,
    ProfileStatus,
    Users,
    Alerts,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            // Scouter Drift Routes
            Routes::DriftCustom => "scouter/drift/custom",
            Routes::DriftPsi => "scouter/drift/psi",
            Routes::DriftSpc => "scouter/drift/spc",

            // Scouter Profile Routes
            Routes::Profile => "scouter/profile",
            Routes::ProfileStatus => "scouter/profile/status",

            // Scouter User Routes
            Routes::Users => "scouter/user",

            // Scouter Alerts Routes
            Routes::Alerts => "scouter/alerts",
        }
    }
}

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
        bootstrap_token: settings.bootstrap_token.clone(),
    })
}

#[derive(Debug, Clone)]
pub struct ScouterApiClient {
    pub client: Client,
    pub base_path: String,
    pub enabled: bool,
    pub bootstrap_token: String,
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
        &self,
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

    /// Create the initial user in scouter
    /// This is used to create the first users shared between scouter and opsml and is only used once
    /// during the initial setup of the system if no users exist
    pub async fn create_initial_user(&self, user: &User) -> Result<Response, ApiError> {
        let user_val = serde_json::to_value(user).map_err(|e| {
            ApiError::Error(format!("Failed to convert user to json with error: {}", e))
        })?;

        // create header to X-Bootstrap-Token
        let mut headers = HeaderMap::new();
        headers.insert(
            "X-Bootstrap-Token",
            self.bootstrap_token.parse().map_err(|e| {
                ApiError::Error(format!("Failed to parse bootstrap token with error: {}", e))
            })?,
        );
        self.request(
            Routes::Users,
            RequestType::Post,
            Some(user_val),
            None,
            Some(headers),
            self.bootstrap_token.clone(),
        )
        .await
    }

    pub async fn delete_user(
        &self,
        username: &str,
        bearer_token: String,
    ) -> Result<Response, ApiError> {
        let url = format!("{}/{}/{}", self.base_path, Routes::Users.as_str(), username);

        self.client
            .delete(url)
            .bearer_auth(&bearer_token)
            .send()
            .await
            .map_err(|e| ApiError::Error(format!("Failed to send request with error: {}", e)))
    }
}
