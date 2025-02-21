use crate::contracts::ArtifactKey;
use crate::{
    cards::CardTable,
    interfaces::{types::DataInterfaceType, ModelType, TaskType},
    DataType, ModelInterfaceType, RegistryType,
};
use chrono::NaiveDateTime;
use opsml_colors::Colorize;
use opsml_error::CardError;
use opsml_semver::VersionType;
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::path::PathBuf;
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
pub struct DeleteCardRequest {
    pub uid: String,
    pub repository: String,
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

#[derive(Debug, Serialize, Deserialize)]
pub struct CardVersionRequest {
    pub name: String,
    pub repository: String,
    pub version: Option<String>,
    pub version_type: VersionType,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
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
    pub tags: Option<Vec<String>>,
    pub limit: Option<i32>,
    pub sort_by_timestamp: Option<bool>,
    pub registry_type: RegistryType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct DataCardClientRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub tags: Vec<String>,
    pub data_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub username: String,
}

impl Default for DataCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            data_type: DataType::NotProvided.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: DataInterfaceType::Base.to_string(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ModelCardClientRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub tags: Vec<String>,
    pub datacard_uid: Option<String>,
    pub data_type: String,
    pub model_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub task_type: String,
    pub username: String,
}

impl Default for ModelCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),

            tags: Vec::new(),
            datacard_uid: None,
            data_type: DataType::NotProvided.to_string(),
            model_type: ModelType::Unknown.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: ModelInterfaceType::Base.to_string(),
            task_type: TaskType::Other.to_string(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ExperimentCardClientRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub tags: Vec<String>,
    pub datacard_uids: Vec<String>,
    pub modelcard_uids: Vec<String>,
    pub experimentcard_uids: Vec<String>,
    pub username: String,
}

impl Default for ExperimentCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            experimentcard_uids: Vec::new(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct AuditCardClientRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub tags: Vec<String>,
    pub approved: bool,
    pub datacard_uids: Vec<String>,
    pub modelcard_uids: Vec<String>,
    pub experimentcard_uids: Vec<String>,
    pub username: String,
}

impl Default for AuditCardClientRecord {
    fn default() -> Self {
        Self {
            uid: "".to_string(),
            created_at: get_utc_datetime(),
            app_env: "development".to_string(),
            name: "".to_string(),
            repository: "".to_string(),
            version: "".to_string(),
            tags: Vec::new(),
            approved: false,
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            experimentcard_uids: Vec::new(),
            username: "guest".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
#[pyclass]
pub enum Card {
    Data(DataCardClientRecord),
    Model(ModelCardClientRecord),
    Experiment(ExperimentCardClientRecord),
    Audit(AuditCardClientRecord),
}

#[pymethods]
impl Card {
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
        }
    }

    #[getter]
    pub fn created_at(&self) -> NaiveDateTime {
        match self {
            Self::Data(card) => card.created_at,
            Self::Model(card) => card.created_at,
            Self::Experiment(card) => card.created_at,
            Self::Audit(card) => card.created_at,
        }
    }

    #[getter]
    pub fn app_env(&self) -> &str {
        match self {
            Self::Data(card) => card.app_env.as_ref(),
            Self::Model(card) => card.app_env.as_ref(),
            Self::Experiment(card) => card.app_env.as_ref(),
            Self::Audit(card) => card.app_env.as_ref(),
        }
    }

    #[getter]
    pub fn name(&self) -> &str {
        match self {
            Self::Data(card) => card.name.as_ref(),
            Self::Model(card) => card.name.as_ref(),
            Self::Experiment(card) => card.name.as_ref(),
            Self::Audit(card) => card.name.as_ref(),
        }
    }

    #[getter]
    pub fn repository(&self) -> &str {
        match self {
            Self::Data(card) => card.repository.as_ref(),
            Self::Model(card) => card.repository.as_ref(),
            Self::Experiment(card) => card.repository.as_ref(),
            Self::Audit(card) => card.repository.as_ref(),
        }
    }

    #[getter]
    pub fn version(&self) -> &str {
        match self {
            Self::Data(card) => card.version.as_ref(),
            Self::Model(card) => card.version.as_ref(),
            Self::Experiment(card) => card.version.as_ref(),
            Self::Audit(card) => card.version.as_ref(),
        }
    }

    #[getter]
    pub fn tags(&self) -> &Vec<String> {
        match self {
            Self::Data(card) => &card.tags,
            Self::Model(card) => &card.tags,
            Self::Experiment(card) => &card.tags,
            Self::Audit(card) => &card.tags,
        }
    }

    #[getter]
    pub fn datacard_uids(&self) -> Option<Vec<&str>> {
        match self {
            Self::Data(card) => Some(vec![&card.uid]),
            Self::Model(card) => card.datacard_uid.as_deref().map(|uid| vec![uid]),
            Self::Experiment(card) => Some(card.datacard_uids.iter().map(String::as_str).collect()),
            Self::Audit(card) => Some(card.datacard_uids.iter().map(String::as_str).collect()),
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
        }
    }

    #[getter]
    pub fn auditcard_uid(&self) -> Option<&str> {
        match self {
            Self::Data(card) => card.auditcard_uid.as_deref(),
            Self::Model(card) => card.auditcard_uid.as_deref(),
            Self::Experiment(_) => None,
            Self::Audit(card) => Some(&card.uid),
        }
    }

    #[getter]
    pub fn interface_type(&self) -> Option<String> {
        match self {
            Self::Data(card) => Some(card.interface_type.to_string()),
            Self::Model(card) => Some(card.interface_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
        }
    }

    #[getter]
    pub fn data_type(&self) -> Option<String> {
        match self {
            Self::Data(card) => Some(card.data_type.to_string()),
            Self::Model(card) => Some(card.data_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
        }
    }

    #[getter]
    pub fn model_type(&self) -> Option<String> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(card.model_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
        }
    }

    #[getter]
    pub fn task_type(&self) -> Option<String> {
        match self {
            Self::Data(_) => None,
            Self::Model(card) => Some(card.task_type.to_string()),
            Self::Experiment(_) => None,
            Self::Audit(_) => None,
        }
    }
}

impl Card {
    pub fn uri(&self) -> Result<PathBuf, CardError> {
        match self {
            Self::Data(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Data,
                    card.repository,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
            Self::Model(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Model,
                    card.repository,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }
            Self::Experiment(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Run,
                    card.repository,
                    card.name,
                    card.version
                );
                Ok(Path::new(&uri).to_path_buf())
            }

            Self::Audit(card) => {
                let uri = format!(
                    "{}/{}/{}/v{}",
                    CardTable::Audit,
                    card.repository,
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
        }
    }
}

#[derive(Tabled)]
struct CardTableEntry {
    created_at: String,
    name: String,
    repository: String,
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
                let repository = card.repository();
                let version = card.version();
                let uid = card.uid();

                CardTableEntry {
                    created_at,
                    name: name.to_string(),
                    repository: repository.to_string(),
                    version: version.to_string(),
                    uid: Colorize::purple(uid),
                }
            })
            .collect();

        let mut table = Table::new(entries);

        table.with(Style::sharp());
        table.modify(Columns::single(0), Width::wrap(20).keep_words(true));
        table.modify(Columns::single(1), Width::wrap(15).keep_words(true));
        table.modify(Columns::single(2), Width::wrap(15).keep_words(true));
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
pub struct CreateCardRequest {
    pub registry_type: RegistryType,
    pub card: Card,
    pub version_request: CardVersionRequest,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateCardResponse {
    pub registered: bool,
    pub version: String,
    pub repository: String,
    pub name: String,
    pub app_env: String,
    pub created_at: NaiveDateTime,
    pub key: ArtifactKey,
}

/// Duplicating card request to be explicit with naming
#[derive(Serialize, Deserialize)]
pub struct UpdateCardRequest {
    pub card: Card,
    pub registry_type: RegistryType,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateCardResponse {
    pub updated: bool,
}
