use axum::http::HeaderMap;
use headers::UserAgent;
use opsml_client::Routes;

use opsml_types::contracts::{AuditStatus, Operation, ResourceType};
use opsml_types::RegistryType;

use std::net::SocketAddr;

#[derive(Debug, Clone)]
pub struct AuditEvent {
    pub username: String,
    pub client_ip: String,
    pub user_agent: String,
    pub operation_type: Operation,
    pub resource_type: ResourceType,
    pub resource_id: String,
    pub status: AuditStatus,
    pub error_message: Option<String>,
    pub metadata: String,
    pub registry_type: RegistryType,
    pub route: Routes,
}

impl AuditEvent {
    pub fn new(
        addr: SocketAddr,
        agent: UserAgent,
        headers: HeaderMap,
        operation_type: Operation,
        resource_type: ResourceType,
        resource_id: String,
        metadata: String,
        registry_type: RegistryType,
        route: Routes,
    ) -> Self {
        Self {
            username: headers
                .get("username")
                .unwrap_or(&"guest".parse().unwrap())
                .to_str()
                .unwrap_or("guest")
                .to_string(),
            client_ip: headers
                .get("X-Forwarded-For")
                .and_then(|hv| hv.to_str().ok())
                .map(|ip| ip.split(',').next().unwrap_or("unknown").to_string())
                .unwrap_or_else(|| addr.ip().to_string()),
            user_agent: agent.to_string(),
            operation_type,
            resource_type,
            resource_id,
            status: AuditStatus::Success,
            error_message: None,
            metadata,
            registry_type,
            route,
        }
    }

    pub fn with_error(mut self, error: impl ToString) -> Self {
        self.status = AuditStatus::Failed;
        self.error_message = Some(error.to_string());
        self
    }
}

#[derive(Debug, Clone)]
pub enum Event {
    Audit(AuditEvent),
    // Add other events as needed
}
