use crate::contracts::ResourceType;
use crate::RegistryType;
use serde::Serialize;
pub trait AuditableRequest: Serialize {
    fn get_resource_id(&self) -> String;
    fn get_metadata(&self) -> String;
    fn get_registry_type(&self) -> Option<RegistryType>;
    fn get_resource_type(&self) -> ResourceType;
}
