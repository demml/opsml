// extension used for various audit-related contexts and routes
use opsml_types::contracts::{
    AuditableRequest, CardQueryArgs, CreateCardRequest, DeleteCardRequest, Operation,
    QueryPageRequest, RegistryStatsRequest, RepositoryRequest, ResourceType, UidRequest,
    UpdateCardRequest, VersionPageRequest,
};
use opsml_types::RegistryType;
use serde::Serialize;

#[derive(Clone, Default)]
pub struct AuditContext {
    pub resource_id: Option<String>,
    pub additional_metadata: Option<String>,
    pub operation: Option<Operation>,
}

#[derive(Debug, Serialize, Clone)]
pub enum AuditableRequestType {
    Uid(UidRequest),
    Delete(DeleteCardRequest),
    Repository(RepositoryRequest),
    Stats(RegistryStatsRequest),
    QueryPage(QueryPageRequest),
    VersionPage(VersionPageRequest),
    CardQuery(CardQueryArgs),
    CreateCard(CreateCardRequest),
    UpdateCard(UpdateCardRequest),
}

impl AuditableRequest for AuditableRequestType {
    fn get_resource_id(&self) -> String {
        match self {
            Self::Uid(req) => req.get_resource_id(),
            Self::Delete(req) => req.get_resource_id(),
            Self::Repository(req) => req.get_resource_id(),
            Self::Stats(req) => req.get_resource_id(),
            Self::QueryPage(req) => req.get_resource_id(),
            Self::VersionPage(req) => req.get_resource_id(),
            Self::CardQuery(req) => req.get_resource_id(),
            Self::CreateCard(req) => req.get_resource_id(),
            Self::UpdateCard(req) => req.get_resource_id(),
        }
    }

    fn get_metadata(&self) -> Result<String, opsml_error::TypeError> {
        match self {
            Self::Uid(req) => req.get_metadata(),
            Self::Delete(req) => req.get_metadata(),
            Self::Repository(req) => req.get_metadata(),
            Self::Stats(req) => req.get_metadata(),
            Self::QueryPage(req) => req.get_metadata(),
            Self::VersionPage(req) => req.get_metadata(),
            Self::CardQuery(req) => req.get_metadata(),
            Self::CreateCard(req) => req.get_metadata(),
            Self::UpdateCard(req) => req.get_metadata(),
        }
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        match self {
            Self::Uid(req) => req.get_registry_type(),
            Self::Delete(req) => req.get_registry_type(),
            Self::Repository(req) => req.get_registry_type(),
            Self::Stats(req) => req.get_registry_type(),
            Self::QueryPage(req) => req.get_registry_type(),
            Self::VersionPage(req) => req.get_registry_type(),
            Self::CardQuery(req) => req.get_registry_type(),
            Self::CreateCard(req) => req.get_registry_type(),
            Self::UpdateCard(req) => req.get_registry_type(),
        }
    }

    fn get_resource_type(&self) -> ResourceType {
        match self {
            Self::Uid(req) => req.get_resource_type(),
            Self::Delete(req) => req.get_resource_type(),
            Self::Repository(req) => req.get_resource_type(),
            Self::Stats(req) => req.get_resource_type(),
            Self::QueryPage(req) => req.get_resource_type(),
            Self::VersionPage(req) => req.get_resource_type(),
            Self::CardQuery(req) => req.get_resource_type(),
            Self::CreateCard(req) => req.get_resource_type(),
            Self::UpdateCard(req) => req.get_resource_type(),
        }
    }

    // Implement other trait methods similarly...
}
