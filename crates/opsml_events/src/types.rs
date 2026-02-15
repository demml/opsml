use axum::http::HeaderMap;
use headers::UserAgent;

use opsml_types::RegistryType;
use opsml_types::contracts::{AuditEvent, AuditStatus, Operation, ResourceType, SpaceNameEvent};

use std::net::SocketAddr;

#[derive(Clone)]
pub struct AuditContext {
    pub resource_id: String,
    pub resource_type: ResourceType,
    pub metadata: String,
    pub operation: Operation,
    pub registry_type: Option<RegistryType>,
    pub access_location: Option<String>,
}

pub fn create_audit_event(
    addr: SocketAddr,
    agent: UserAgent,
    headers: HeaderMap,
    route: String,
    context: AuditContext,
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
        operation: context.operation,
        resource_type: context.resource_type,
        resource_id: context.resource_id,
        access_location: context.access_location,
        status: AuditStatus::Success,
        error_message: None,
        metadata: context.metadata,
        registry_type: context.registry_type,
        route,
    }
}

#[derive(Debug, Clone)]
pub enum Event {
    Audit(AuditEvent),
    SpaceName(SpaceNameEvent),
    // Add other events as needed
}
