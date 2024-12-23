use crate::cards::types::RegistryType;
use crate::shared::PyHelperFuncs;
use chrono::NaiveDateTime;
use opsml_colors::Colorize;
use opsml_utils::VersionType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::LazyLock;
use tabled::settings::{
    format::Format,
    object::{Columns, Rows},
    Alignment, Color, Style, Width,
};
use tabled::{Table, Tabled};

#[derive(Serialize, Deserialize)]
pub struct UidRequest {
    pub uid: String,
    pub registry_type: RegistryType,
}

#[derive(Serialize, Deserialize)]
pub struct UidResponse {
    pub exists: bool,
}

#[derive(Serialize, Deserialize)]
pub struct RepositoryRequest {
    pub registry_type: RegistryType,
}

#[derive(Serialize, Deserialize)]
pub struct RepositoryResponse {
    pub repositories: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub struct RegistryStatsRequest {
    pub registry_type: RegistryType,
    pub search_term: Option<String>,
}

// RegistryStatsResponse is sourced from sql schema

#[derive(Serialize, Deserialize)]
pub struct QueryPageRequest {
    pub registry_type: RegistryType,
    pub sort_by: Option<String>,
    pub repository: Option<String>,
    pub search_term: Option<String>,
    pub page: Option<i32>,
}

// QueryPageResponse is sourced from sql schema

#[derive(Serialize, Deserialize)]
pub struct CardVersionRequest {
    pub registry_type: RegistryType,
    pub name: String,
    pub repository: String,
    pub version: Option<String>,
    pub version_type: VersionType,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CardVersionResponse {
    pub version: String,
}

/// Arguments for querying cards
///
/// # Fields
///
/// * `uid` - The unique identifier of the card
/// * `name` - The name of the card
/// * `repository` - The repository of the card
/// * `version` - The version of the card
/// * `max_date` - The maximum date of the card
/// * `tags` - The tags of the card
/// * `limit` - The maximum number of cards to return
/// * `query_terms` - The query terms to search for
/// * `sort_by_timestamp` - Whether to sort by timestamp

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct CardQueryArgs {
    pub uid: Option<String>,
    pub name: Option<String>,
    pub repository: Option<String>,
    pub version: Option<String>,
    pub max_date: Option<String>,
    pub tags: Option<HashMap<String, String>>,
    pub limit: Option<i32>,
    pub sort_by_timestamp: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ListCardRequest {
    pub uid: Option<String>,
    pub name: Option<String>,
    pub repository: Option<String>,
    pub version: Option<String>,
    pub max_date: Option<String>,
    pub tags: Option<HashMap<String, String>>,
    pub limit: Option<i32>,
    pub sort_by_timestamp: Option<bool>,
    pub registry_type: RegistryType,
}

impl Default for ListCardRequest {
    fn default() -> Self {
        Self {
            uid: None,
            name: None,
            repository: None,
            version: None,
            max_date: None,
            tags: None,
            limit: None,
            sort_by_timestamp: None,
            registry_type: RegistryType::Data,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct DataCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub app_env: Option<String>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub contact: String,
    pub tags: HashMap<String, String>,
    pub data_type: String,
    pub runcard_uid: Option<String>,
    pub pipelinecard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: Option<String>,
}

impl Default for DataCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            app_env: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            contact: "".to_string(),
            tags: HashMap::new(),
            data_type: "".to_string(),
            runcard_uid: None,
            pipelinecard_uid: None,
            auditcard_uid: None,
            interface_type: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ModelCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub app_env: Option<String>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub contact: String,
    pub tags: HashMap<String, String>,
    pub datacard_uid: Option<String>,
    pub sample_data_type: String,
    pub model_type: String,
    pub runcard_uid: Option<String>,
    pub pipelinecard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: Option<String>,
    pub task_type: Option<String>,
}

impl Default for ModelCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            app_env: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            contact: "".to_string(),
            tags: HashMap::new(),
            datacard_uid: None,
            sample_data_type: "".to_string(),
            model_type: "".to_string(),
            runcard_uid: None,
            pipelinecard_uid: None,
            auditcard_uid: None,
            interface_type: None,
            task_type: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct RunCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub app_env: Option<String>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub contact: String,
    pub tags: HashMap<String, String>,
    pub datacard_uids: Option<Vec<String>>,
    pub modelcard_uids: Option<Vec<String>>,
    pub pipelinecard_uid: Option<String>,
    pub project: String,
    pub artifact_uris: Option<HashMap<String, String>>,
    pub compute_environment: Option<HashMap<String, String>>,
}

impl Default for RunCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            app_env: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            contact: "".to_string(),
            tags: HashMap::new(),
            datacard_uids: None,
            modelcard_uids: None,
            pipelinecard_uid: None,
            project: "".to_string(),
            artifact_uris: None,
            compute_environment: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct AuditCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub app_env: Option<String>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub contact: String,
    pub tags: HashMap<String, String>,
    pub approved: bool,
    pub datacard_uids: Option<Vec<String>>,
    pub modelcard_uids: Option<Vec<String>>,
    pub runcard_uids: Option<Vec<String>>,
}

impl Default for AuditCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            app_env: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            contact: "".to_string(),
            tags: HashMap::new(),
            approved: false,
            datacard_uids: None,
            modelcard_uids: None,
            runcard_uids: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct PipelineCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub app_env: Option<String>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub contact: String,
    pub tags: HashMap<String, String>,
    pub pipeline_code_uri: String,
    pub datacard_uids: Option<Vec<String>>,
    pub modelcard_uids: Option<Vec<String>>,
    pub runcard_uids: Option<Vec<String>>,
}

impl Default for PipelineCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            app_env: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            contact: "".to_string(),
            tags: HashMap::new(),
            pipeline_code_uri: "".to_string(),
            datacard_uids: None,
            modelcard_uids: None,
            runcard_uids: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ProjectCardClientRecord {
    pub uid: Option<String>,
    pub created_at: Option<NaiveDateTime>,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub project_id: i32,
}

impl Default for ProjectCardClientRecord {
    fn default() -> Self {
        Self {
            uid: None,
            created_at: None,
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            project_id: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
#[pyclass]
pub enum Card {
    Data(DataCardClientRecord),
    Model(ModelCardClientRecord),
    Run(RunCardClientRecord),
    Audit(AuditCardClientRecord),
    Pipeline(PipelineCardClientRecord),
    Project(ProjectCardClientRecord),
}

#[pymethods]
impl Card {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[getter]
    pub fn uid(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.uid.as_deref(),
            Self::Model(card) => card.uid.as_deref(),
            Self::Run(card) => card.uid.as_deref(),
            Self::Audit(card) => card.uid.as_deref(),
            Self::Pipeline(card) => card.uid.as_deref(),
            Self::Project(card) => card.uid.as_deref(),
        }
    }

    #[getter]
    pub fn created_at(&self) -> Option<NaiveDateTime> {
        match self {
            Self::Data(card) => card.created_at,
            Self::Model(card) => card.created_at,
            Self::Run(card) => card.created_at,
            Self::Audit(card) => card.created_at,
            Self::Pipeline(card) => card.created_at,
            Self::Project(card) => card.created_at,
        }
    }

    #[getter]
    pub fn app_env(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.app_env.as_deref(),
            Self::Model(card) => card.app_env.as_deref(),
            Self::Run(card) => card.app_env.as_deref(),
            Self::Audit(card) => card.app_env.as_deref(),
            Self::Pipeline(card) => card.app_env.as_deref(),
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn name(&self) -> &str {
        match self {
            Self::Data(card) => card.name.as_ref(),
            Self::Model(card) => card.name.as_ref(),
            Self::Run(card) => card.name.as_ref(),
            Self::Audit(card) => card.name.as_ref(),
            Self::Pipeline(card) => card.name.as_ref(),
            Self::Project(card) => card.name.as_ref(),
        }
    }

    #[getter]
    pub fn repository(&self) -> &str {
        match self {
            Self::Data(card) => card.repository.as_ref(),
            Self::Model(card) => card.repository.as_ref(),
            Self::Run(card) => card.repository.as_ref(),
            Self::Audit(card) => card.repository.as_ref(),
            Self::Pipeline(card) => card.repository.as_ref(),
            Self::Project(card) => card.repository.as_ref(),
        }
    }

    #[getter]
    pub fn version(&self) -> &str {
        match self {
            Self::Data(card) => card.version.as_ref(),
            Self::Model(card) => card.version.as_ref(),
            Self::Run(card) => card.version.as_ref(),
            Self::Audit(card) => card.version.as_ref(),
            Self::Pipeline(card) => card.version.as_ref(),
            Self::Project(card) => card.version.as_ref(),
        }
    }

    #[getter]
    pub fn contact(&self) -> &str {
        match self {
            Self::Data(card) => card.contact.as_ref(),
            Self::Model(card) => card.contact.as_ref(),
            Self::Run(card) => card.contact.as_ref(),
            Self::Audit(card) => card.contact.as_ref(),
            Self::Pipeline(card) => card.contact.as_ref(),
            Self::Project(_) => "",
        }
    }

    #[getter]
    pub fn tags(&self) -> &HashMap<String, String> {
        match self {
            Self::Data(card) => &card.tags,
            Self::Model(card) => &card.tags,
            Self::Run(card) => &card.tags,
            Self::Audit(card) => &card.tags,
            Self::Pipeline(card) => &card.tags,
            Self::Project(_) => {
                static EMPTY_MAP: LazyLock<HashMap<String, String>> = LazyLock::new(HashMap::new);
                &EMPTY_MAP
            }
        }
    }

    #[getter]
    pub fn datacard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(card) => card.uid.as_deref().map(|uid| vec![uid]),
            Self::Model(card) => card.datacard_uid.as_deref().map(|uid| vec![uid]),
            Self::Run(card) => card
                .datacard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Audit(card) => card
                .datacard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Pipeline(card) => card
                .datacard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn modelcard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => card.uid.as_deref().map(|uid| vec![uid]),
            Self::Run(card) => card
                .modelcard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Audit(card) => card
                .modelcard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Pipeline(card) => card
                .modelcard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn runcard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(card) => card.runcard_uid.as_deref().map(|uid| vec![uid]),
            Self::Model(card) => card.runcard_uid.as_deref().map(|uid| vec![uid]),
            Self::Run(card) => card.uid.as_deref().map(|uid| vec![uid]),
            Self::Audit(card) => card
                .runcard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Pipeline(card) => card
                .runcard_uids
                .as_ref()
                .map(|uids| uids.iter().map(String::as_str).collect()),
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn pipelinecard_uid(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.pipelinecard_uid.as_deref(),
            Self::Model(card) => card.pipelinecard_uid.as_deref(),
            Self::Run(card) => card.pipelinecard_uid.as_deref(),
            Self::Audit(_) => None,
            Self::Pipeline(card) => card.uid.as_deref(),
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn auditcard_uid(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.auditcard_uid.as_deref(),
            Self::Model(card) => card.auditcard_uid.as_deref(),
            Self::Run(_) => None,
            Self::Audit(card) => card.uid.as_deref(),
            Self::Pipeline(_) => None,
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn interface_type(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.interface_type.as_deref(),
            Self::Model(card) => card.interface_type.as_deref(),
            Self::Run(_) => None,
            Self::Audit(_) => None,
            Self::Pipeline(_) => None,
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn data_type(&self) -> Option<&str> {
        match self {
            Self::Data(card) => Some(card.data_type.as_str()),
            Self::Model(card) => Some(card.sample_data_type.as_str()),
            Self::Run(_) => None,
            Self::Audit(_) => None,
            Self::Pipeline(_) => None,
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn model_type(&self) -> Option<&str> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(card.model_type.as_str()),
            Self::Run(_) => None,
            Self::Audit(_) => None,
            Self::Pipeline(_) => None,
            Self::Project(_) => None,
        }
    }

    #[getter]
    pub fn task_type(&self) -> Option<&str> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => card.task_type.as_deref(),
            Self::Run(_) => None,
            Self::Audit(_) => None,
            Self::Pipeline(_) => None,
            Self::Project(_) => None,
        }
    }
}

#[derive(Tabled)]
struct CardTableEntry {
    created_at: String,
    name: String,
    repository: String,
    contact: String,
    version: String,
    uid: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct CardList {
    #[pyo3(get)]
    pub cards: Vec<Card>,
}

#[pymethods]
impl CardList {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn as_table(&self) {
        let entries: Vec<CardTableEntry> = self
            .cards
            .iter()
            .map(|card| {
                let created_at = card.created_at().unwrap().to_string();
                let name = card.name();
                let repository = card.repository();
                let contact = card.contact();
                let version = card.version();
                let uid = card.uid();

                CardTableEntry {
                    created_at,
                    name: name.to_string(),
                    repository: repository.to_string(),
                    contact: contact.to_string(),
                    version: version.to_string(),
                    uid: Colorize::purple(uid.unwrap()),
                }
            })
            .collect();

        let mut table = Table::new(entries);

        table.with(Style::sharp());
        table.modify(Columns::single(0), Width::wrap(20).keep_words(true));
        table.modify(Columns::single(1), Width::wrap(15).keep_words(true));
        table.modify(Columns::single(2), Width::wrap(15).keep_words(true));
        table.modify(Columns::single(3), Width::wrap(15).keep_words(true));
        table.modify(Columns::single(4), Width::wrap(30).keep_words(true));
        table.modify(Columns::single(5), Width::wrap(50));
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

#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct CardInfo {
    #[pyo3(get)]
    pub name: Option<String>,

    #[pyo3(get)]
    pub repository: Option<String>,

    #[pyo3(get)]
    pub contact: Option<String>,

    #[pyo3(get)]
    pub uid: Option<String>,

    #[pyo3(get)]
    pub version: Option<String>,

    #[pyo3(get)]
    pub tags: Option<HashMap<String, String>>,
}

#[pymethods]
impl CardInfo {
    #[new]
    #[pyo3(signature = (name=None, repository=None, contact=None, uid=None, version=None, tags=None))]
    pub fn new(
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        uid: Option<String>,
        version: Option<String>,
        tags: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            name,
            repository,
            contact,
            uid,
            version,
            tags,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn set_env(&self) {
        // if check name, repo and contact. If any is set, set environment variable
        // if name is set, set OPSML_RUNTIME_NAME
        // if repository is set, set OPSML_RUNTIME_REPOSITORY
        // if contact is set, set OPSML_RUNTIME_CONTACT

        if let Some(name) = &self.name {
            std::env::set_var("OPSML_RUNTIME_NAME", name);
        }

        if let Some(repo) = &self.repository {
            std::env::set_var("OPSML_RUNTIME_REPOSITORY", repo);
        }

        if let Some(contact) = &self.contact {
            std::env::set_var("OPSML_RUNTIME_CONTACT", contact);
        }
    }

    // primarily used for checking and testing. Do not write .pyi file for this method
    pub fn get_vars(&self) -> HashMap<String, String> {
        // check if OPSML_RUNTIME_NAME, OPSML_RUNTIME_REPOSITORY, OPSML_RUNTIME_CONTACT are set
        // Print out the values if they are set

        let name = std::env::var("OPSML_RUNTIME_NAME").unwrap_or_default();
        let repo = std::env::var("OPSML_RUNTIME_REPOSITORY").unwrap_or_default();
        let contact = std::env::var("OPSML_RUNTIME_CONTACT").unwrap_or_default();

        // print
        let mut map = HashMap::new();
        map.insert("OPSML_RUNTIME_NAME".to_string(), name);
        map.insert("OPSML_RUNTIME_REPOSITORY".to_string(), repo);
        map.insert("OPSML_RUNTIME_CONTACT".to_string(), contact);

        map
    }
}

impl CardInfo {
    pub fn get_value_by_name(&self, name: &str) -> &Option<String> {
        match name {
            "name" => &self.name,
            "repository" => &self.repository,
            "contact" => &self.contact,
            "uid" => &self.uid,
            "version" => &self.version,
            _ => &None,
        }
    }
}

impl FromPyObject<'_> for CardInfo {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let name = ob.getattr("name").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let repository = ob.getattr("repository").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let contact = ob.getattr("contact").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let version = ob.getattr("version").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let uid = ob.getattr("uid").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let tags = ob.getattr("tags").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<HashMap<String, String>>()?))
            }
        })?;

        Ok(CardInfo {
            name,
            repository,
            contact,
            uid,
            version,
            tags,
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateCardRequest {
    pub registry_type: RegistryType,
    pub card: Card,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateCardResponse {
    pub registered: bool,
    pub uid: String,
}

/// Duplicating card request to be explicit with naming
#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateCardRequest {
    pub registry_type: RegistryType,
    pub card: Card,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateCardResponse {
    pub updated: bool,
}
