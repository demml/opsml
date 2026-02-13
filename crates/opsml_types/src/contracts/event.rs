use crate::RegistryType;
use crate::contracts::{AuditStatus, Operation, ResourceType};

#[derive(Debug, Clone)]
pub struct AuditEvent {
    pub username: String,
    pub client_ip: String,
    pub user_agent: String,
    pub operation: Operation,
    pub resource_type: ResourceType,
    pub resource_id: String,
    pub access_location: Option<String>,
    pub status: AuditStatus,
    pub error_message: Option<String>,
    pub metadata: String,
    pub registry_type: Option<RegistryType>,
    pub route: String,
}

impl Default for AuditEvent {
    fn default() -> Self {
        Self {
            username: "guest".to_string(),
            client_ip: "unknown".to_string(),
            user_agent: "unknown".to_string(),
            operation: Operation::Write,
            resource_type: ResourceType::File,
            resource_id: "unknown".to_string(),
            access_location: None,
            status: AuditStatus::Success,
            error_message: None,
            metadata: "unknown".to_string(),
            registry_type: Some(RegistryType::Model),
            route: "unknown".to_string(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct SpaceNameEvent {
    pub space: String,
    pub name: String,
    pub registry_type: RegistryType,
}
