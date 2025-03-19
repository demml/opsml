use chrono::NaiveDateTime;
use opsml_error::error::VersionError;
use opsml_types::cards::{CardTable, ParameterValue};
use opsml_types::{CommonKwargs, DataType, ModelType, RegistryType};
use opsml_utils::utils::get_utc_datetime;
use semver::{BuildMetadata, Prerelease, Version};
use serde::{Deserialize, Serialize};
use sqlx::{prelude::FromRow, types::Json};
use std::env;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MetricRecord {
    pub experiment_uid: String,
    pub name: String,
    pub value: f64,
    pub step: Option<i32>,
    pub timestamp: Option<i64>,
    pub created_at: Option<NaiveDateTime>,
    pub idx: Option<i32>,
}

impl MetricRecord {
    pub fn new(
        experiment_uid: String,
        name: String,
        value: f64,
        step: Option<i32>,
        timestamp: Option<i64>,
    ) -> Self {
        MetricRecord {
            experiment_uid,
            name,
            value,
            step,
            timestamp,
            created_at: None,
            idx: None,
        }
    }
}

impl Default for MetricRecord {
    fn default() -> Self {
        MetricRecord {
            experiment_uid: Uuid::new_v4().to_string(),
            name: CommonKwargs::Undefined.to_string(),
            value: 0.0,
            step: None,
            timestamp: None,
            created_at: None,
            idx: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ParameterRecord {
    pub experiment_uid: String,
    pub name: String,
    pub value: Json<ParameterValue>,
}

impl ParameterRecord {
    pub fn new(experiment_uid: String, name: String, value: ParameterValue) -> Self {
        ParameterRecord {
            experiment_uid,
            name,
            value: Json(value),
        }
    }
}

impl Default for ParameterRecord {
    fn default() -> Self {
        ParameterRecord {
            experiment_uid: Uuid::new_v4().to_string(),
            name: CommonKwargs::Undefined.to_string(),
            value: Json(ParameterValue::Int(0)),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct VersionResult {
    pub created_at: NaiveDateTime,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
}

impl VersionResult {
    pub fn to_version(&self) -> Result<Version, VersionError> {
        let mut version = Version::new(self.major as u64, self.minor as u64, self.patch as u64);

        if self.pre_tag.is_some() {
            version.pre = Prerelease::new(self.pre_tag.as_ref().unwrap())
                .map_err(|e| VersionError::InvalidPreRelease(format!("{}", e)))?;
        }

        if self.build_tag.is_some() {
            version.build = BuildMetadata::new(self.build_tag.as_ref().unwrap())
                .map_err(|e| VersionError::InvalidBuild(format!("{}", e)))?;
        }

        Ok(version)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Repository {
    pub repository: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct QueryStats {
    pub nbr_names: i32,
    pub nbr_repositories: i32,
    pub nbr_versions: i32,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct CardSummary {
    pub repository: String,
    pub name: String,
    pub version: String,
    pub versions: i64,
    pub updated_at: NaiveDateTime,
    pub created_at: NaiveDateTime,
    pub row_num: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct DataCardRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub data_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl DataCardRecord {
    pub fn new(
        name: String,
        repository: String,
        version: Version,
        tags: Vec<String>,
        data_type: String,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        interface_type: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = Uuid::new_v4().to_string();

        DataCardRecord {
            uid,
            created_at,
            app_env,
            name,
            repository,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            data_type,
            experimentcard_uid,
            auditcard_uid,
            interface_type,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Data,
            self.repository,
            self.name,
            self.version
        )
    }
}

impl Default for DataCardRecord {
    fn default() -> Self {
        DataCardRecord {
            uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            repository: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            data_type: DataType::NotProvided.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: CommonKwargs::Undefined.to_string(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ModelCardRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub datacard_uid: Option<String>,
    pub data_type: String,
    pub model_type: String,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub interface_type: String,
    pub task_type: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl ModelCardRecord {
    pub fn new(
        name: String,
        repository: String,
        version: Version,
        tags: Vec<String>,
        datacard_uid: Option<String>,
        data_type: String,
        model_type: String,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        interface_type: String,
        task_type: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = Uuid::new_v4().to_string();

        ModelCardRecord {
            uid,
            created_at,
            app_env,
            name,
            repository,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            datacard_uid,
            data_type,
            model_type,
            experimentcard_uid,
            auditcard_uid,
            interface_type,
            task_type,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Model,
            self.repository,
            self.name,
            self.version
        )
    }
}

impl Default for ModelCardRecord {
    fn default() -> Self {
        ModelCardRecord {
            uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            repository: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            datacard_uid: None,
            data_type: DataType::NotProvided.to_string(),
            model_type: ModelType::Unknown.to_string(),
            experimentcard_uid: None,
            auditcard_uid: None,
            interface_type: CommonKwargs::Undefined.to_string(),
            task_type: CommonKwargs::Undefined.to_string(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExperimentCardRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub datacard_uids: Json<Vec<String>>,
    pub modelcard_uids: Json<Vec<String>>,
    pub promptcard_uids: Json<Vec<String>>,
    pub experimentcard_uids: Json<Vec<String>>,
    pub username: String,
}

impl Default for ExperimentCardRecord {
    fn default() -> Self {
        ExperimentCardRecord {
            uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            repository: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            datacard_uids: Json(Vec::new()),
            modelcard_uids: Json(Vec::new()),
            promptcard_uids: Json(Vec::new()),
            experimentcard_uids: Json(Vec::new()),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[allow(clippy::too_many_arguments)]
impl ExperimentCardRecord {
    pub fn new(
        name: String,
        repository: String,
        version: Version,
        tags: Vec<String>,
        datacard_uids: Vec<String>,
        modelcard_uids: Vec<String>,
        promptcard_uids: Vec<String>,
        experimentcard_uids: Vec<String>,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = Uuid::new_v4().to_string();

        ExperimentCardRecord {
            uid,
            created_at,
            app_env,
            name,
            repository,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            datacard_uids: Json(datacard_uids),
            modelcard_uids: Json(modelcard_uids),
            promptcard_uids: Json(promptcard_uids),
            experimentcard_uids: Json(experimentcard_uids),
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Experiment,
            self.repository,
            self.name,
            self.version
        )
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AuditCardRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub approved: bool,
    pub datacard_uids: Json<Vec<String>>,
    pub modelcard_uids: Json<Vec<String>>,
    pub experimentcard_uids: Json<Vec<String>>,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl AuditCardRecord {
    pub fn new(
        name: String,
        repository: String,
        version: Version,
        tags: Vec<String>,
        approved: bool,
        datacard_uids: Vec<String>,
        modelcard_uids: Vec<String>,
        experimentcard_uids: Vec<String>,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = Uuid::new_v4().to_string();

        AuditCardRecord {
            uid,
            created_at,
            app_env,
            name,
            repository,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            approved,
            datacard_uids: Json(datacard_uids),
            modelcard_uids: Json(modelcard_uids),
            experimentcard_uids: Json(experimentcard_uids),
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Audit,
            self.repository,
            self.name,
            self.version
        )
    }
}

impl Default for AuditCardRecord {
    fn default() -> Self {
        AuditCardRecord {
            uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            repository: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            approved: false,
            datacard_uids: Json(Vec::new()),
            modelcard_uids: Json(Vec::new()),
            experimentcard_uids: Json(Vec::new()),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct PromptCardRecord {
    pub uid: String,
    pub created_at: NaiveDateTime,
    pub app_env: String,
    pub name: String,
    pub repository: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl PromptCardRecord {
    pub fn new(
        name: String,
        repository: String,
        version: Version,
        tags: Vec<String>,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = Uuid::new_v4().to_string();

        PromptCardRecord {
            uid,
            created_at,
            app_env,
            name,
            repository,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            experimentcard_uid,
            auditcard_uid,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Prompt,
            self.repository,
            self.name,
            self.version
        )
    }
}

impl Default for PromptCardRecord {
    fn default() -> Self {
        PromptCardRecord {
            uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            repository: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            experimentcard_uid: None,
            auditcard_uid: None,
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

// create enum that takes vec of cards
// TODO: There should also be a client side enum that matches this (don't want to install opsml_sql on client)
#[derive(Debug, Serialize, Deserialize)]
pub enum CardResults {
    Data(Vec<DataCardRecord>),
    Model(Vec<ModelCardRecord>),
    Experiment(Vec<ExperimentCardRecord>),
    Audit(Vec<AuditCardRecord>),
    Prompt(Vec<PromptCardRecord>),
}

impl CardResults {
    pub fn len(&self) -> usize {
        match self {
            CardResults::Data(cards) => cards.len(),
            CardResults::Model(cards) => cards.len(),
            CardResults::Experiment(cards) => cards.len(),
            CardResults::Audit(cards) => cards.len(),
            CardResults::Prompt(cards) => cards.len(),
        }
    }
    pub fn is_empty(&self) -> bool {
        match self {
            CardResults::Data(cards) => cards.is_empty(),
            CardResults::Model(cards) => cards.is_empty(),
            CardResults::Experiment(cards) => cards.is_empty(),
            CardResults::Audit(cards) => cards.is_empty(),
            CardResults::Prompt(cards) => cards.is_empty(),
        }
    }
    pub fn to_json(&self) -> Vec<String> {
        match self {
            CardResults::Data(cards) => cards
                .iter()
                .map(|card| serde_json::to_string_pretty(card).unwrap())
                .collect(),
            CardResults::Model(cards) => cards
                .iter()
                .map(|card| serde_json::to_string_pretty(card).unwrap())
                .collect(),
            CardResults::Experiment(cards) => cards
                .iter()
                .map(|card| serde_json::to_string_pretty(card).unwrap())
                .collect(),
            CardResults::Audit(cards) => cards
                .iter()
                .map(|card| serde_json::to_string_pretty(card).unwrap())
                .collect(),
            CardResults::Prompt(cards) => cards
                .iter()
                .map(|card| serde_json::to_string_pretty(card).unwrap())
                .collect(),
        }
    }
}

#[derive(Debug)]
pub enum ServerCard {
    Data(DataCardRecord),
    Model(ModelCardRecord),
    Experiment(ExperimentCardRecord),
    Audit(AuditCardRecord),
    Prompt(PromptCardRecord),
}

impl ServerCard {
    pub fn uid(&self) -> &str {
        match self {
            ServerCard::Data(card) => card.uid.as_str(),
            ServerCard::Model(card) => card.uid.as_str(),
            ServerCard::Experiment(card) => card.uid.as_str(),
            ServerCard::Audit(card) => card.uid.as_str(),
            ServerCard::Prompt(card) => card.uid.as_str(),
        }
    }

    pub fn registry_type(&self) -> String {
        match self {
            ServerCard::Data(_) => RegistryType::Data.to_string(),
            ServerCard::Model(_) => RegistryType::Model.to_string(),
            ServerCard::Experiment(_) => RegistryType::Experiment.to_string(),
            ServerCard::Audit(_) => RegistryType::Audit.to_string(),
            ServerCard::Prompt(_) => RegistryType::Prompt.to_string(),
        }
    }

    pub fn version(&self) -> String {
        match self {
            ServerCard::Data(card) => card.version.clone(),
            ServerCard::Model(card) => card.version.clone(),
            ServerCard::Experiment(card) => card.version.clone(),
            ServerCard::Audit(card) => card.version.clone(),
            ServerCard::Prompt(card) => card.version.clone(),
        }
    }

    pub fn repository(&self) -> String {
        match self {
            ServerCard::Data(card) => card.repository.clone(),
            ServerCard::Model(card) => card.repository.clone(),
            ServerCard::Experiment(card) => card.repository.clone(),
            ServerCard::Audit(card) => card.repository.clone(),
            ServerCard::Prompt(card) => card.repository.clone(),
        }
    }

    pub fn name(&self) -> String {
        match self {
            ServerCard::Data(card) => card.name.clone(),
            ServerCard::Model(card) => card.name.clone(),
            ServerCard::Experiment(card) => card.name.clone(),
            ServerCard::Audit(card) => card.name.clone(),
            ServerCard::Prompt(card) => card.name.clone(),
        }
    }

    pub fn uri(&self) -> String {
        match self {
            ServerCard::Data(card) => card.uri(),
            ServerCard::Model(card) => card.uri(),
            ServerCard::Experiment(card) => card.uri(),
            ServerCard::Audit(card) => card.uri(),
            ServerCard::Prompt(card) => card.uri(),
        }
    }

    pub fn app_env(&self) -> String {
        match self {
            ServerCard::Data(card) => card.app_env.clone(),
            ServerCard::Model(card) => card.app_env.clone(),
            ServerCard::Experiment(card) => card.app_env.clone(),
            ServerCard::Audit(card) => card.app_env.clone(),
            ServerCard::Prompt(card) => card.app_env.clone(),
        }
    }

    pub fn created_at(&self) -> NaiveDateTime {
        match self {
            ServerCard::Data(card) => card.created_at,
            ServerCard::Model(card) => card.created_at,
            ServerCard::Experiment(card) => card.created_at,
            ServerCard::Audit(card) => card.created_at,
            ServerCard::Prompt(card) => card.created_at,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HardwareMetricsRecord {
    pub experiment_uid: String,
    pub created_at: NaiveDateTime,
    pub cpu_percent_utilization: f32,
    pub cpu_percent_per_core: Json<Vec<f32>>,
    pub free_memory: i64,
    pub total_memory: i64,
    pub used_memory: i64,
    pub available_memory: i64,
    pub used_percent_memory: f64,
    pub bytes_recv: i64,
    pub bytes_sent: i64,
}

impl Default for HardwareMetricsRecord {
    fn default() -> Self {
        HardwareMetricsRecord {
            experiment_uid: Uuid::new_v4().to_string(),
            created_at: get_utc_datetime(),
            cpu_percent_utilization: 0.0,
            cpu_percent_per_core: Json(Vec::new()),
            free_memory: 0,
            total_memory: 0,
            used_memory: 0,
            available_memory: 0,
            used_percent_memory: 0.0,
            bytes_recv: 0,
            bytes_sent: 0,
        }
    }
}

#[derive(Serialize, Deserialize, Clone)]
pub struct User {
    pub id: Option<i32>,
    pub created_at: NaiveDateTime,
    pub active: bool,
    pub username: String,
    pub password_hash: String,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
    pub role: String,
    pub refresh_token: Option<String>,
}

impl User {
    pub fn new(
        username: String,
        password_hash: String,
        permissions: Option<Vec<String>>,
        group_permissions: Option<Vec<String>>,
        role: Option<String>,
    ) -> Self {
        let created_at = get_utc_datetime();

        User {
            id: None,
            created_at,
            active: true,
            username,
            password_hash,
            permissions: permissions.unwrap_or(vec!["read".to_string(), "write".to_string()]),
            group_permissions: group_permissions.unwrap_or(vec!["user".to_string()]),
            role: role.unwrap_or("user".to_string()),
            refresh_token: None,
        }
    }
}

impl std::fmt::Debug for User {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("User")
            .field("id", &self.id)
            .field("username", &self.username)
            .field("active", &self.active)
            .field("password_hash", &"[redacted]")
            .field("permissions", &"[redacted]")
            .field("group_permissions", &"[redacted]")
            .finish()
    }
}
