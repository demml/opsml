use crate::cards::CardStatus;
use crate::contracts::{
    ArtifactKey, AuditableRequest, DeploymentConfig, ResourceType, ServiceConfig, ServiceMetadata,
    ServiceType,
};
use crate::error::TypeError;
use crate::{
    cards::CardTable,
    interfaces::{types::DataInterfaceType, ModelType, TaskType},
    DataType, ModelInterfaceType, RegistryType,
};
use chrono::{DateTime, Utc};
use opsml_colors::Colorize;
use opsml_semver::VersionType;
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use pyo3::prelude::*;
use semver::Version;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use tabled::settings::{format::Format, object::Rows, Alignment, Color, Style};
use tabled::{Table, Tabled};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct UidRequest {
    pub uid: String,
    pub registry_type: RegistryType,
}

impl AuditableRequest for UidRequest {
    fn get_resource_id(&self) -> String {
        self.uid.clone()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize UidRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeleteCardRequest {
    pub uid: String,
    pub space: String,
    pub registry_type: RegistryType,
}

impl AuditableRequest for DeleteCardRequest {
    fn get_resource_id(&self) -> String {
        self.uid.clone()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize DeleteCardRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Serialize, Deserialize)]
pub struct UidResponse {
    pub exists: bool,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RegistrySpaceRequest {
    pub registry_type: RegistryType,
}

impl AuditableRequest for RegistrySpaceRequest {
    fn get_resource_id(&self) -> String {
        self.registry_type.to_string()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize RegistrySpaceRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Serialize, Deserialize)]
pub struct CardSpaceResponse {
    pub spaces: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub struct CardTagsResponse {
    pub tags: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CrudSpaceRequest {
    pub space: String,
    pub description: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CrudSpaceResponse {
    pub success: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct SpaceRecord {
    pub space: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SpaceNameRecord {
    pub space: String,
    pub name: String,
    pub registry_type: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SpaceRecordResponse {
    pub spaces: Vec<SpaceRecord>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SpaceStats {
    pub space: String,
    pub model_count: i64,
    pub data_count: i64,
    pub prompt_count: i64,
    pub experiment_count: i64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SpaceStatsResponse {
    pub stats: Vec<SpaceStats>,
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct RegistryStatsRequest {
    pub registry_type: RegistryType,
    pub search_term: Option<String>,

    #[serde(default)]
    pub spaces: Vec<String>,

    #[serde(default)]
    pub tags: Vec<String>,
}

impl AuditableRequest for RegistryStatsRequest {
    fn get_resource_id(&self) -> String {
        self.registry_type.to_string()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize RegistryStatsRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

/// Cursor for paginating through card results with search state
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct CardCursor {
    pub offset: i32,
    pub limit: i32,
    pub sort_by: String,
    pub search_term: Option<String>,
    #[serde(default)]
    pub spaces: Vec<String>,
    #[serde(default)]
    pub tags: Vec<String>,
}

impl CardCursor {
    /// Create a new cursor with search criteria
    pub fn new(
        offset: i32,
        limit: i32,
        sort_by: String,
        search_term: Option<String>,
        spaces: Vec<String>,
        tags: Vec<String>,
    ) -> Self {
        Self {
            offset,
            limit,
            sort_by,
            search_term,
            spaces,
            tags,
        }
    }

    pub fn next(&self) -> Self {
        Self {
            offset: self.offset + self.limit,
            limit: self.limit,
            sort_by: self.sort_by.clone(),
            search_term: self.search_term.clone(),
            spaces: self.spaces.clone(),
            tags: self.tags.clone(),
        }
    }

    pub fn previous(&self) -> Self {
        Self {
            offset: (self.offset - self.limit).max(0),
            limit: self.limit,
            sort_by: self.sort_by.clone(),
            search_term: self.search_term.clone(),
            spaces: self.spaces.clone(),
            tags: self.tags.clone(),
        }
    }

    /// Check if this is the first page
    pub fn is_first_page(&self) -> bool {
        self.offset == 0
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct QueryPageRequest {
    pub registry_type: RegistryType,
    pub page: Option<i32>,
    pub cursor: Option<CardCursor>,
    pub limit: Option<i32>,
    pub sort_by: Option<String>,
    pub search_term: Option<String>,
    #[serde(default)]
    pub spaces: Vec<String>,
    #[serde(default)]
    pub tags: Vec<String>,
}

impl QueryPageRequest {
    /// Extract or build cursor from request parameters
    pub fn get_cursor(&self, default_limit: i32, default_sort_by: &str) -> CardCursor {
        if let Some(cursor) = &self.cursor {
            cursor.clone()
        } else {
            let limit = self.limit.unwrap_or(default_limit);
            let offset = self.page.map(|p| (p - 1) * limit).unwrap_or(0);
            let sort_by = self
                .sort_by
                .clone()
                .unwrap_or_else(|| default_sort_by.to_string());

            CardCursor::new(
                offset,
                limit,
                sort_by,
                self.search_term.clone(),
                self.spaces.clone(),
                self.tags.clone(),
            )
        }
    }
}

impl AuditableRequest for QueryPageRequest {
    fn get_resource_id(&self) -> String {
        self.registry_type.to_string()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize QueryPageRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

// ...existing code...

/// Cursor for paginating through version results
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct VersionCursor {
    pub offset: i32,
    pub limit: i32,
    pub space: String,
    pub name: String,
}

impl VersionCursor {
    /// Create a new version cursor
    pub fn new(offset: i32, limit: i32, space: String, name: String) -> Self {
        Self {
            offset,
            limit,
            space,
            name,
        }
    }

    pub fn next(&self) -> Self {
        Self {
            offset: self.offset + self.limit,
            limit: self.limit,
            space: self.space.clone(),
            name: self.name.clone(),
        }
    }

    pub fn previous(&self) -> Self {
        Self {
            offset: (self.offset - self.limit).max(0),
            limit: self.limit,
            space: self.space.clone(),
            name: self.name.clone(),
        }
    }

    /// Check if this is the first page
    pub fn is_first_page(&self) -> bool {
        self.offset == 0
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct VersionPageRequest {
    pub registry_type: RegistryType,
    pub space: String,
    pub name: String,
    pub cursor: Option<VersionCursor>,
    pub limit: Option<i32>,
}

impl VersionPageRequest {
    /// Extract or build cursor from request parameters
    pub fn get_cursor(&self, default_limit: i32) -> VersionCursor {
        if let Some(cursor) = &self.cursor {
            cursor.clone()
        } else {
            VersionCursor::new(
                0,
                self.limit.unwrap_or(default_limit),
                self.space.clone(),
                self.name.clone(),
            )
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CardVersionRequest {
    pub name: String,
    pub space: String,
    pub version: Option<String>,
    pub version_type: VersionType,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct ServiceQueryArgs {
    pub space: Option<String>,
    pub name: Option<String>,
    pub tags: Option<Vec<String>>,
    pub service_type: ServiceType,
}

impl ServiceQueryArgs {
    pub fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize ServiceQueryArgs: {e}"))
    }
}

/// Arguments for querying cards
///
/// # Fields
///
/// * `uid` - The unique identifier of the card
/// * `name` - The name of the card
/// * `space` - The space of the card
/// * `version` - The version of the card
/// * `max_date` - The maximum date of the card
/// * `tags` - The tags of the card
/// * `limit` - The maximum number of cards to return
/// * `sort_by_timestamp` - Whether to sort by timestamp
/// * `service_type` - The service type of the card (only for ServiceCards)

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct CardQueryArgs {
    pub uid: Option<String>,
    pub name: Option<String>,
    pub space: Option<String>,
    pub version: Option<String>,
    pub max_date: Option<String>,
    pub tags: Option<Vec<String>>,
    pub limit: Option<i32>,
    pub sort_by_timestamp: Option<bool>,
    pub registry_type: RegistryType,
}

impl AuditableRequest for CardQueryArgs {
    fn get_resource_id(&self) -> String {
        self.uid.clone().unwrap_or_default()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize CardQueryArgs: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct DataCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub tags: Vec<String>,
    pub data_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub opsml_version: String,
    pub username: String,
}

impl Default for DataCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            space: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            data_type: DataType::NotProvided.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: DataInterfaceType::Base.to_string(),
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ModelCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub tags: Vec<String>,
    pub datacard_uid: Option<String>,
    pub data_type: String,
    pub model_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub task_type: String,
    pub opsml_version: String,
    pub username: String,
}

impl Default for ModelCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            space: "".to_string(),
            version: "".to_string(),

            tags: Vec::new(),
            datacard_uid: None,
            data_type: DataType::NotProvided.to_string(),
            model_type: ModelType::Unknown.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: ModelInterfaceType::Base.to_string(),
            task_type: TaskType::Undefined.to_string(),
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ExperimentCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub tags: Vec<String>,
    pub datacard_uids: Vec<String>,
    pub modelcard_uids: Vec<String>,
    pub promptcard_uids: Vec<String>,
    pub service_card_uids: Vec<String>,
    pub experimentcard_uids: Vec<String>,
    pub opsml_version: String,
    pub username: String,
    pub status: CardStatus,
}

impl Default for ExperimentCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            space: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            promptcard_uids: Vec::new(),
            service_card_uids: Vec::new(),
            experimentcard_uids: Vec::new(),
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
            status: CardStatus::Ok,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct AuditCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub tags: Vec<String>,
    pub approved: bool,
    pub datacard_uids: Vec<String>,
    pub modelcard_uids: Vec<String>,
    pub experimentcard_uids: Vec<String>,
    pub opsml_version: String,
    pub username: String,
}

impl Default for AuditCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            space: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            approved: false,
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            experimentcard_uids: Vec::new(),
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct PromptCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub tags: Vec<String>,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub opsml_version: String,
    pub username: String,
}

impl Default for PromptCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            space: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            experimentcard_uid: None,
            auditcard_uid: None,
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ServiceCardClientRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub space: String,
    pub name: String,
    pub version: String,
    pub cards: Vec<CardEntry>,
    pub opsml_version: String,
    pub service_type: String,
    pub metadata: Option<ServiceMetadata>,
    pub deployment: Option<Vec<DeploymentConfig>>,
    pub service_config: Option<ServiceConfig>,
    pub username: String,
    pub tags: Vec<String>,
}

impl Default for ServiceCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            space: "".to_string(),
            name: "".to_string(),
            version: "".to_string(),
            opsml_version: opsml_version::version(),
            username: "guest".to_string(),
            service_type: ServiceType::Api.to_string(),
            metadata: None,
            deployment: None,
            service_config: None,
            cards: Vec::new(),
            tags: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
#[pyclass]
pub enum CardRecord {
    Data(DataCardClientRecord),
    Model(ModelCardClientRecord),
    Experiment(ExperimentCardClientRecord),
    Audit(AuditCardClientRecord),
    Prompt(PromptCardClientRecord),
    Service(ServiceCardClientRecord),
}

#[pymethods]
impl CardRecord {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[getter]
    pub fn uid(&self) -> &str {
        match self {
            Self::Data(card) => &card.uid,
            Self::Model(card) => &card.uid,
            Self::Experiment(card) => &card.uid,
            Self::Audit(card) => &card.uid,
            Self::Prompt(card) => &card.uid,
            Self::Service(card) => &card.uid,
        }
    }

    #[getter]
    pub fn created_at(&self) -> DateTime<Utc> {
        match self {
            Self::Data(card) => card.created_at,
            Self::Model(card) => card.created_at,
            Self::Experiment(card) => card.created_at,
            Self::Audit(card) => card.created_at,
            Self::Prompt(card) => card.created_at,
            Self::Service(card) => card.created_at,
        }
    }

    #[getter]
    pub fn app_env(&self) -> &str {
        match self {
            Self::Data(card) => card.app_env.as_ref(),
            Self::Model(card) => card.app_env.as_ref(),
            Self::Experiment(card) => card.app_env.as_ref(),
            Self::Audit(card) => card.app_env.as_ref(),
            Self::Prompt(card) => card.app_env.as_ref(),
            Self::Service(card) => card.app_env.as_ref(),
        }
    }

    #[getter]
    pub fn name(&self) -> &str {
        match self {
            Self::Data(card) => card.name.as_ref(),
            Self::Model(card) => card.name.as_ref(),
            Self::Experiment(card) => card.name.as_ref(),
            Self::Audit(card) => card.name.as_ref(),
            Self::Prompt(card) => card.name.as_ref(),
            Self::Service(card) => card.name.as_ref(),
        }
    }

    #[getter]
    pub fn space(&self) -> &str {
        match self {
            Self::Data(card) => card.space.as_ref(),
            Self::Model(card) => card.space.as_ref(),
            Self::Experiment(card) => card.space.as_ref(),
            Self::Audit(card) => card.space.as_ref(),
            Self::Prompt(card) => card.space.as_ref(),
            Self::Service(card) => card.space.as_ref(),
        }
    }

    #[getter]
    pub fn version(&self) -> &str {
        match self {
            Self::Data(card) => card.version.as_ref(),
            Self::Model(card) => card.version.as_ref(),
            Self::Experiment(card) => card.version.as_ref(),
            Self::Audit(card) => card.version.as_ref(),
            Self::Prompt(card) => card.version.as_ref(),
            Self::Service(card) => card.version.as_ref(),
        }
    }

    #[getter]
    pub fn tags(&self) -> &Vec<String> {
        static EMPTY_TAGS: Vec<String> = Vec::new();
        match self {
            Self::Data(card) => &card.tags,
            Self::Model(card) => &card.tags,
            Self::Experiment(card) => &card.tags,
            Self::Audit(card) => &card.tags,
            Self::Prompt(card) => &card.tags,
            Self::Service(_card) => &EMPTY_TAGS,
        }
    }

    #[getter]
    pub fn datacard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(card) => Some(vec![&card.uid]),
            Self::Model(card) => card.datacard_uid.as_deref().map(|uid| vec![uid]),
            Self::Experiment(card) => Some(card.datacard_uids.iter().map(String::as_str).collect()),
            Self::Audit(card) => Some(card.datacard_uids.iter().map(String::as_str).collect()),
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn modelcard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(vec![&card.uid]),
            Self::Experiment(card) => {
                Some(card.modelcard_uids.iter().map(String::as_str).collect())
            }
            Self::Audit(card) => Some(card.modelcard_uids.iter().map(String::as_str).collect()),
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn experimentcard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(card) => card.experimentcard_uid.as_deref().map(|uid| vec![uid]),
            Self::Model(card) => card.experimentcard_uid.as_deref().map(|uid| vec![uid]),
            Self::Experiment(card) => Some(vec![&card.uid]),
            Self::Audit(card) => Some(
                card.experimentcard_uids
                    .iter()
                    .map(String::as_str)
                    .collect(),
            ),
            Self::Prompt(card) => Some(vec![&card.experimentcard_uid.as_deref().unwrap()]),
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn auditcard_uid(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.auditcard_uid.as_deref(),
            Self::Model(card) => card.auditcard_uid.as_deref(),
            Self::Experiment(_) => None,
            Self::Audit(card) => Some(&card.uid),
            Self::Prompt(card) => card.auditcard_uid.as_deref(),
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn interface_type(&self) -> Option<String> {
        match self {
            Self::Data(card) => Some(card.interface_type.to_string()),
            Self::Model(card) => Some(card.interface_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn data_type(&self) -> Option<String> {
        match self {
            Self::Data(card) => Some(card.data_type.to_string()),
            Self::Model(card) => Some(card.data_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn model_type(&self) -> Option<String> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(card.model_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }

    #[getter]
    pub fn task_type(&self) -> Option<String> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(card.task_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
            Self::Prompt(_) => None,
            Self::Service(_) => None,
        }
    }
}

impl CardRecord {
    pub fn cards(&self) -> Option<Vec<CardEntry>> {
        match self {
            Self::Data(_) => None,
            Self::Model(_) => None,
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
            Self::Prompt(_) => None,
            Self::Service(card) => Some(card.cards.clone()),
        }
    }

    pub fn uri(&self) -> Result<PathBuf, TypeError> {
        match self {
            Self::Data(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Data,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
            Self::Model(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Model,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
            Self::Experiment(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Experiment,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }

            Self::Audit(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Audit,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }

            Self::Prompt(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Prompt,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
            Self::Service(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Service,
                    card.space,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
        }
    }

    pub fn registry_type(&self) -> RegistryType {
        match self {
            Self::Data(_) => RegistryType::Data,
            Self::Model(_) => RegistryType::Model,
            Self::Experiment(_) => RegistryType::Experiment,
            Self::Audit(_) => RegistryType::Audit,
            Self::Prompt(_) => RegistryType::Prompt,
            Self::Service(_) => RegistryType::Service,
        }
    }
}

/// Sort cards by their semver
/// # Arguments
/// * `cards` - A mutable reference to a vector of CardRecord
/// * `reverse` - A boolean indicating whether to sort in reverse order
pub fn sort_cards_by_version(cards: &mut [CardRecord], reverse: bool) {
    cards.sort_by(|a, b| {
        let a_version = Version::parse(a.version()).unwrap();
        let b_version = Version::parse(b.version()).unwrap();
        a_version.cmp(&b_version)
    });

    if reverse {
        cards.reverse();
    }
}

#[derive(Tabled)]
struct CardTableEntry {
    created_at: String,
    name: String,
    space: String,
    version: String,
    uid: String,
}

#[pyclass]
struct CardListIter {
    inner: std::vec::IntoIter<CardRecord>,
}

#[pymethods]
impl CardListIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<CardRecord> {
        slf.inner.next()
    }
}

#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct CardList {
    #[pyo3(get)]
    pub cards: Vec<CardRecord>,
}

#[pymethods]
impl CardList {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn __getitem__(&self, index: usize) -> Option<CardRecord> {
        self.cards.get(index).cloned()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<CardListIter>> {
        let iter = CardListIter {
            inner: slf.cards.clone().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __len__(&self) -> usize {
        self.cards.len()
    }

    pub fn as_table(&self) {
        let entries: Vec<CardTableEntry> = self
            .cards
            .iter()
            .map(|card| {
                let created_at = card.created_at().to_string();
                let name = card.name();
                let space = card.space();
                let version = card.version();
                let uid = card.uid();

                CardTableEntry {
                    created_at,
                    name: name.to_string(),
                    space: space.to_string(),
                    version: version.to_string(),
                    uid: Colorize::purple(uid),
                }
            })
            .collect();

        let mut table = Table::new(entries);

        table.with(Style::sharp());
        table.modify(
            Rows::new(0..1),
            (
                Format::content(Colorize::green),
                Alignment::center(),
                Color::BOLD,
            ),
        );

        println!("{}", &table);
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CreateCardRequest {
    pub registry_type: RegistryType,
    pub card: CardRecord,
    pub version_request: CardVersionRequest,
}

impl AuditableRequest for CreateCardRequest {
    fn get_resource_id(&self) -> String {
        self.card.uid().to_string()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize CreateCardRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateCardResponse {
    pub registered: bool,
    pub version: String,
    pub space: String,
    pub name: String,
    pub app_env: String,
    pub created_at: DateTime<Utc>,
    pub key: ArtifactKey,
}

/// Duplicating card request to be explicit with naming
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct UpdateCardRequest {
    pub card: CardRecord,
    pub registry_type: RegistryType,
}

impl AuditableRequest for UpdateCardRequest {
    fn get_resource_id(&self) -> String {
        self.card.uid().to_string()
    }

    fn get_metadata(&self) -> String {
        serde_json::to_string(self)
            .unwrap_or_else(|e| format!("Failed to serialize UpdateCardRequest: {e}"))
    }

    fn get_registry_type(&self) -> Option<RegistryType> {
        Some(self.registry_type.clone())
    }

    fn get_resource_type(&self) -> ResourceType {
        ResourceType::Database
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateCardResponse {
    pub updated: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CardEntry {
    pub registry_type: RegistryType,
    pub uid: Option<String>,
    pub version: Option<String>,
    pub alias: String,
}
