use crate::core::error::ServerError;
use crate::core::user::schema::CreateUserRequest;
use anyhow::Result;
use opsml_client::error::ApiClientError;
use opsml_settings::config::ScouterSettings;
use opsml_sql::schemas::User;
use opsml_types::api::RequestType;
/// Route for debugging information
use reqwest::Response;
use reqwest::{header::HeaderMap, Client};
use serde_json::Value;
use tracing::error;

const X_BOOTSTRAP_TOKEN: &str = "x-bootstrap-token";

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum Routes {
    DriftGenAITask,
    DriftGenAIWorkflow,
    DriftCustom,
    DriftPsi,
    DriftSpc,
    GenAIWorkflow,
    GenAITask,
    GenAIRecords,
    Profile,
    ProfileStatus,
    Users,
    Alerts,
    Healthcheck,
    TracePage,
    TraceSpans,
    TraceMetrics,
    TagEntity,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            // Scouter Drift Routes
            Routes::DriftCustom => "scouter/drift/custom",
            Routes::DriftPsi => "scouter/drift/psi",
            Routes::DriftSpc => "scouter/drift/spc",
            Routes::DriftGenAIWorkflow => "scouter/drift/genai/workflow",
            Routes::DriftGenAITask => "scouter/drift/genai/task",

            // Scouter GenAI Routes
            Routes::GenAIWorkflow => "scouter/genai/page/workflow",
            Routes::GenAITask => "scouter/genai/task",
            Routes::GenAIRecords => "scouter/genai/page/record",

            // Scouter Profile Routes
            Routes::Profile => "scouter/profile",
            Routes::ProfileStatus => "scouter/profile/status",

            // Scouter User Routes
            Routes::Users => "scouter/user",

            // Scouter Alerts Routes
            Routes::Alerts => "scouter/alerts",

            // Scouter Healthcheck
            Routes::Healthcheck => "scouter/healthcheck",

            // Scouter Trace Routes
            Routes::TracePage => "scouter/trace/paginated",
            Routes::TraceSpans => "scouter/trace/spans",
            Routes::TraceMetrics => "scouter/trace/metrics",
            Routes::TagEntity => "scouter/tags/entity",
        }
    }
}

const TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone)]
pub struct ScouterApiClient {
    pub client: Client,
    pub base_path: String,
    pub enabled: bool,
    pub bootstrap_token: String,
}

impl ScouterApiClient {
    pub async fn new(settings: &ScouterSettings) -> Result<Self> {
        let client = Self::build_http_client()?;

        let client = Self {
            client,
            base_path: settings.server_uri.clone(),
            enabled: false,
            bootstrap_token: settings.bootstrap_token.clone(),
        };

        // scouter not integrated - exist early
        if client.base_path.is_empty() {
            return Ok(client);
        }

        client.check_and_enable_service().await
    }

    fn build_http_client() -> Result<Client, ServerError> {
        Client::builder()
            .timeout(std::time::Duration::from_secs(TIMEOUT_SECS))
            .build()
            .map_err(ServerError::CreateClientError)
    }

    async fn check_and_enable_service(mut self) -> Result<Self> {
        let healthcheck = self.healthcheck(&self.bootstrap_token).await?;
        self.enabled = healthcheck.status().is_success();

        if !self.enabled {
            error!(
                "Scouter is configured but healthcheck failed with status: {}",
                healthcheck.status()
            );
        }

        Ok(self)
    }

    async fn _request(
        &self,
        route: Routes,
        request_type: RequestType,
        body_params: Option<Value>,
        query_string: Option<String>,
        headers: Option<HeaderMap>,
        bearer_token: &str,
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
                    .bearer_auth(bearer_token)
                    .send()
                    .await?
            }
            RequestType::Post => {
                self.client
                    .post(url)
                    .headers(headers)
                    .json(&body_params)
                    .bearer_auth(bearer_token)
                    .send()
                    .await?
            }
            RequestType::Put => {
                self.client
                    .put(url)
                    .headers(headers)
                    .json(&body_params)
                    .bearer_auth(bearer_token)
                    .send()
                    .await?
            }
            RequestType::Delete => {
                let url = if let Some(query_string) = query_string {
                    format!("{url}?{query_string}")
                } else {
                    url
                };
                self.client
                    .delete(url)
                    .headers(headers)
                    .bearer_auth(bearer_token)
                    .send()
                    .await?
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
        bearer_token: &str,
    ) -> Result<Response, ApiClientError> {
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
    pub async fn create_initial_user(
        &self,
        user: &User,
        password: &str,
    ) -> Result<Response, ApiClientError> {
        let user_request = CreateUserRequest {
            username: user.username.clone(),
            password: password.to_string(),
            email: user.email.clone(),
            permissions: Some(user.permissions.clone()),
            group_permissions: Some(user.group_permissions.clone()),
            role: Some(user.role.clone()),
            active: Some(user.active),
        };

        let user_val = serde_json::to_value(user_request)?;

        // create header to X-Bootstrap-Token
        let mut headers = HeaderMap::new();
        headers.insert(X_BOOTSTRAP_TOKEN, self.bootstrap_token.parse()?);
        self.request(
            Routes::Users,
            RequestType::Post,
            Some(user_val),
            None,
            Some(headers),
            &self.bootstrap_token,
        )
        .await
    }

    pub async fn delete_user(
        &self,
        username: &str,
        bearer_token: &str,
    ) -> Result<Response, ApiClientError> {
        let url = format!("{}/{}/{}", self.base_path, Routes::Users.as_str(), username);

        Ok(self
            .client
            .delete(url)
            .bearer_auth(bearer_token)
            .send()
            .await?)
    }

    pub async fn healthcheck(&self, bearer_token: &str) -> Result<Response, ApiClientError> {
        let url = format!("{}/{}", self.base_path, Routes::Healthcheck.as_str());

        Ok(self
            .client
            .get(url)
            .bearer_auth(bearer_token)
            .send()
            .await?)
    }
}

pub async fn build_scouter_http_client(settings: &ScouterSettings) -> Result<ScouterApiClient> {
    ScouterApiClient::new(settings).await
}
