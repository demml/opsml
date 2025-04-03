use axum::http::HeaderMap;
use headers::UserAgent;
use opsml_client::Routes;

use opsml_types::contracts::{AuditEvent, AuditStatus, Operation, ResourceType};
use opsml_types::RegistryType;

use std::net::SocketAddr;

pub fn create_audit_record(
    addr: SocketAddr,
    agent: UserAgent,
    headers: HeaderMap,
    operation_type: Operation,
    resource_type: ResourceType,
    resource_id: String,
    access_location: Option<String>,
    metadata: String,
    registry_type: RegistryType,
    route: Routes,
) -> AuditEvent {
    AuditEvent {
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
        access_location,
        status: AuditStatus::Success,
        error_message: None,
        metadata,
        registry_type,
        route,
    }
}

#[derive(Debug, Clone)]
pub enum Event {
    Audit(AuditEvent),
    // Add other events as needed
}
