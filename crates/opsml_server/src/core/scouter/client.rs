use crate::core::error::ServerError;
use crate::core::user::schema::CreateUserRequest;
use anyhow::Result;
use opsml_client::error::ApiClientError;
use opsml_settings::config::ScouterSettings;
use opsml_sql::schemas::User;
use opsml_types::api::RequestType;
/// Route for debugging information
use reqwest::Response;
use reqwest::{Client, header::HeaderMap};
use serde_json::Value;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use tracing::{error, info};

const X_BOOTSTRAP_TOKEN: &str = "x-bootstrap-token";

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum Routes {
    DriftAgentTask,
    DriftAgentWorkflow,
    DriftCustom,
    DriftPsi,
    DriftSpc,
    AgentWorkflow,
    AgentTask,
    AgentRecords,
    Profile,
    ProfileStatus,
    Users,
    Alerts,
    Healthcheck,
    TracePage,
    TraceSpans,
    TraceMetrics,
    TagEntity,
    // Trace extensions
    TraceSpansFilters,
    // Profile extensions
    Profiles,
    // Observability
    ObservabilityMetrics,
    // GenAI
    GenAiTokenMetrics,
    GenAiOperations,
    GenAiModels,
    GenAiAgents,
    GenAiTools,
    GenAiErrors,
    GenAiSpans,
    GenAiConversation,
    GenAiAgentMetrics,
    GenAiToolMetrics,
}

impl Routes {
    pub fn as_str(&self) -> &str {
        match self {
            // Scouter Drift Routes
            Routes::DriftCustom => "scouter/drift/custom",
            Routes::DriftPsi => "scouter/drift/psi",
            Routes::DriftSpc => "scouter/drift/spc",
            Routes::DriftAgentWorkflow => "scouter/drift/agent/workflow",
            Routes::DriftAgentTask => "scouter/drift/agent/task",

            // Scouter Agent Routes
            Routes::AgentWorkflow => "scouter/agent/page/workflow",
            Routes::AgentTask => "scouter/agent/task",
            Routes::AgentRecords => "scouter/agent/page/record",

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

            // Trace extensions
            Routes::TraceSpansFilters => "scouter/trace/spans/filters",

            // Profile extensions
            Routes::Profiles => "scouter/profiles",

            // Observability
            Routes::ObservabilityMetrics => "scouter/observability/metrics",

            // GenAI
            Routes::GenAiTokenMetrics => "scouter/genai/metrics/tokens",
            Routes::GenAiOperations => "scouter/genai/metrics/operations",
            Routes::GenAiModels => "scouter/genai/metrics/models",
            Routes::GenAiAgents => "scouter/genai/metrics/agents",
            Routes::GenAiTools => "scouter/genai/metrics/tools",
            Routes::GenAiErrors => "scouter/genai/metrics/errors",
            Routes::GenAiSpans => "scouter/genai/spans",
            Routes::GenAiConversation => "scouter/genai/conversation",
            Routes::GenAiAgentMetrics => "scouter/genai/agent/metrics",
            Routes::GenAiToolMetrics => "scouter/genai/tool/metrics",
        }
    }
}

const TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone)]
pub struct ScouterApiClient {
    pub client: Client,
    pub base_path: String,
    pub enabled: Arc<AtomicBool>,
    pub bootstrap_token: String,
}

impl ScouterApiClient {
    pub fn is_enabled(&self) -> bool {
        self.enabled.load(Ordering::Relaxed)
    }
}

impl ScouterApiClient {
    pub async fn new(settings: &ScouterSettings) -> Result<Self> {
        let client = Self::build_http_client()?;

        let client = Self {
            client,
            base_path: settings.server_uri.clone(),
            enabled: Arc::new(AtomicBool::new(false)),
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

    async fn check_and_enable_service(self) -> Result<Self> {
        match self.healthcheck(&self.bootstrap_token).await {
            Ok(healthcheck) => {
                let ok = healthcheck.status().is_success();
                self.enabled.store(ok, Ordering::Relaxed);
                if !ok {
                    error!(
                        "Scouter is configured but healthcheck failed with status: {}",
                        healthcheck.status()
                    );
                }
            }
            Err(e) => {
                error!("Scouter healthcheck request failed (Scouter may be down): {e}");
                self.enabled.store(false, Ordering::Relaxed);
            }
        }

        Ok(self)
    }

    /// Spawn a background task that periodically pings Scouter's healthcheck endpoint
    /// and updates `enabled` in-place.  All clones of this client share the same
    /// `Arc<AtomicBool>`, so `AppState` sees the change automatically.
    pub fn spawn_health_watcher(&self) {
        if self.base_path.is_empty() {
            return;
        }

        let client = self.clone();
        tokio::spawn(async move {
            let mut ticker = tokio::time::interval(tokio::time::Duration::from_secs(5));
            ticker.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);

            loop {
                ticker.tick().await;

                let is_up = client
                    .healthcheck(&client.bootstrap_token)
                    .await
                    .map(|r| r.status().is_success())
                    .unwrap_or(false);

                let was_enabled = client.enabled.load(Ordering::Relaxed);
                client.enabled.store(is_up, Ordering::Relaxed);

                if is_up && !was_enabled {
                    info!("✅ Scouter is now online");
                } else if !is_up && was_enabled {
                    error!("❌ Scouter went offline");
                }
            }
        });
    }

    fn append_query(url: String, query_string: Option<&str>) -> String {
        match query_string {
            Some(query) if !query.is_empty() => format!("{url}?{query}"),
            _ => url,
        }
    }

    async fn execute_request(
        &self,
        request_type: RequestType,
        url: String,
        headers: HeaderMap,
        body_params: Option<Value>,
        bearer_token: &str,
    ) -> Result<Response, ApiClientError> {
        let request = match request_type {
            RequestType::Get => self.client.get(url).headers(headers),
            RequestType::Post => self.client.post(url).headers(headers).json(&body_params),
            RequestType::Put => self.client.put(url).headers(headers).json(&body_params),
            RequestType::Delete => self.client.delete(url).headers(headers),
        };

        Ok(request.bearer_auth(bearer_token).send().await?)
    }

    fn build_route_url(&self, route: &Routes, query_string: Option<&str>) -> String {
        let base = format!("{}/{}", self.base_path.trim_end_matches('/'), route.as_str());
        Self::append_query(base, query_string)
    }

    fn build_route_url_with_path_segments(
        &self,
        route: &Routes,
        path_segments: &[&str],
        query_string: Option<&str>,
    ) -> Result<String, ApiClientError> {
        let base = format!("{}/{}", self.base_path.trim_end_matches('/'), route.as_str());
        let mut url = reqwest::Url::parse(&base).map_err(|e| {
            ApiClientError::ServerError(format!("Failed to parse scouter route url: {e}"))
        })?;

        {
            let mut segments = url.path_segments_mut().map_err(|_| {
                ApiClientError::ServerError("Failed to set scouter route path segments".to_string())
            })?;
            for segment in path_segments {
                segments.push(segment);
            }
        }

        if let Some(query) = query_string.filter(|query| !query.is_empty()) {
            url.set_query(Some(query));
        }

        Ok(url.into())
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
        let url = self.build_route_url(&route, query_string.as_deref());
        self.execute_request(request_type, url, headers, body_params, bearer_token)
            .await
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
        self._request(
            route,
            request_type,
            body_params,
            query_params,
            headers,
            bearer_token,
        )
        .await
    }

    pub async fn request_with_path(
        &self,
        route: Routes,
        path_segments: &[&str],
        request_type: RequestType,
        body_params: Option<Value>,
        query_params: Option<String>,
        headers: Option<HeaderMap>,
        bearer_token: &str,
    ) -> Result<Response, ApiClientError> {
        let headers = headers.unwrap_or_default();
        let url = self.build_route_url_with_path_segments(
            &route,
            path_segments,
            query_params.as_deref(),
        )?;

        self.execute_request(request_type, url, headers, body_params, bearer_token)
            .await
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

#[cfg(test)]
mod tests {
    use super::*;
    use mockito::Matcher;
    use std::sync::Arc;
    use std::sync::atomic::AtomicBool;

    fn test_client(base_path: String) -> ScouterApiClient {
        ScouterApiClient {
            client: Client::new(),
            base_path,
            enabled: Arc::new(AtomicBool::new(true)),
            bootstrap_token: "bootstrap-token".to_string(),
        }
    }

    #[tokio::test]
    async fn test_request_post_forwards_query_and_body() {
        let mut server = mockito::Server::new_async().await;
        let _mock = server
            .mock("POST", "/scouter/profile")
            .match_query(Matcher::UrlEncoded("space".into(), "ml".into()))
            .match_body(Matcher::Json(serde_json::json!({ "active": true })))
            .with_status(200)
            .with_body("{}")
            .create_async()
            .await;

        let client = test_client(server.url());
        let response = client
            .request(
                Routes::Profile,
                RequestType::Post,
                Some(serde_json::json!({ "active": true })),
                Some("space=ml".to_string()),
                None,
                "token",
            )
            .await
            .expect("request should succeed");

        assert_eq!(response.status(), reqwest::StatusCode::OK);
    }

    #[tokio::test]
    async fn test_request_put_forwards_query_and_body() {
        let mut server = mockito::Server::new_async().await;
        let _mock = server
            .mock("PUT", "/scouter/profile/status")
            .match_query(Matcher::UrlEncoded("dry_run".into(), "true".into()))
            .match_body(Matcher::Json(
                serde_json::json!({ "active": false, "space": "ml" }),
            ))
            .with_status(200)
            .with_body("{}")
            .create_async()
            .await;

        let client = test_client(server.url());
        let response = client
            .request(
                Routes::ProfileStatus,
                RequestType::Put,
                Some(serde_json::json!({ "active": false, "space": "ml" })),
                Some("dry_run=true".to_string()),
                None,
                "token",
            )
            .await
            .expect("request should succeed");

        assert_eq!(response.status(), reqwest::StatusCode::OK);
    }

    #[tokio::test]
    async fn test_request_with_path_encodes_path_segments() {
        let mut server = mockito::Server::new_async().await;
        let _mock = server
            .mock("GET", "/scouter/genai/conversation/a%2Fb")
            .with_status(200)
            .with_body("{}")
            .create_async()
            .await;

        let client = test_client(server.url());
        let response = client
            .request_with_path(
                Routes::GenAiConversation,
                &["a/b"],
                RequestType::Get,
                None,
                None,
                None,
                "token",
            )
            .await
            .expect("request should succeed");

        assert_eq!(response.status(), reqwest::StatusCode::OK);
    }
}
