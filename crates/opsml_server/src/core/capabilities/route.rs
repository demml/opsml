use crate::core::state::AppState;
use anyhow::Result;
use axum::{Json, Router, extract::State, routing::get};
use serde::Serialize;
use std::sync::Arc;
use utoipa::ToSchema;

const REGISTRY_TYPES: &[&str] = &[
    "data",
    "model",
    "experiment",
    "prompt",
    "service",
    "skill",
    "tool",
    "subagent",
];

#[derive(Serialize, ToSchema)]
pub struct FeaturesInfo {
    pub scouter_enabled: bool,
    pub sso_enabled: bool,
    pub openapi_spec: &'static str,
    pub swagger_ui: &'static str,
}

#[derive(Serialize, ToSchema)]
pub struct DocumentationInfo {
    pub list_docs: &'static str,
    pub search_docs: &'static str,
    pub list_examples: &'static str,
}

#[derive(Serialize, ToSchema)]
pub struct AgenticInfo {
    pub marketplace_map: &'static str,
    pub agent_invoke: &'static str,
    pub skill_latest: &'static str,
    pub tool_latest: &'static str,
}

#[derive(Serialize, ToSchema)]
pub struct AuthInfo {
    pub auth_type: &'static str,
    pub login_endpoint: &'static str,
}

#[derive(Serialize, ToSchema)]
pub struct CapabilitiesResponse {
    pub api_version: &'static str,
    pub server_version: &'static str,
    pub features: FeaturesInfo,
    pub registry_types: &'static [&'static str],
    pub documentation: DocumentationInfo,
    pub agentic: AgenticInfo,
    pub auth: AuthInfo,
}

#[utoipa::path(
    get,
    path = "/opsml/api/v1/capabilities",
    responses(
        (status = 200, description = "Server capabilities and endpoint index", body = CapabilitiesResponse),
    ),
    tag = "capabilities"
)]
pub async fn capabilities(State(state): State<Arc<AppState>>) -> Json<CapabilitiesResponse> {
    Json(CapabilitiesResponse {
        api_version: "1.0.0",
        server_version: env!("CARGO_PKG_VERSION"),
        features: FeaturesInfo {
            scouter_enabled: state.scouter_client.is_enabled(),
            sso_enabled: state.auth_manager.sso_provider.is_some(),
            openapi_spec: "/opsml/api/v1/openapi.json",
            swagger_ui: "/opsml/api/v1/docs/ui",
        },
        registry_types: REGISTRY_TYPES,
        documentation: DocumentationInfo {
            list_docs: "/opsml/api/v1/docs",
            search_docs: "/opsml/api/v1/docs/search?q={query}",
            list_examples: "/opsml/api/v1/examples",
        },
        agentic: AgenticInfo {
            marketplace_map: "/opsml/api/v1/map/{space}",
            agent_invoke: "/opsml/api/v1/agent/{id}/invoke",
            skill_latest: "/opsml/api/v1/skill/{space}/{name}",
            tool_latest: "/opsml/api/v1/tool/{space}/{name}",
        },
        auth: AuthInfo {
            auth_type: "jwt_bearer",
            login_endpoint: "/opsml/api/auth/login",
        },
    })
}

pub async fn get_capabilities_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    Ok(Router::new().route(&format!("{prefix}/capabilities"), get(capabilities)))
}
