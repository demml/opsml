use crate::error::SqlError;
use chrono::{DateTime, Utc};
use opsml_semver::error::VersionError;
use opsml_types::cards::{CardTable, ParameterValue};
use opsml_types::contracts::{
    ArtifactRecord, AuditCardClientRecord, CardEntry, CardRecord, DataCardClientRecord,
    ExperimentCardClientRecord, ModelCardClientRecord, PromptCardClientRecord,
    ServiceCardClientRecord,
};
use opsml_types::{CommonKwargs, DataType, ModelType, RegistryType};
use opsml_utils::create_uuid7;
use opsml_utils::utils::get_utc_datetime;
use semver::{BuildMetadata, Prerelease, Version};
use serde::{Deserialize, Serialize};
use serde_json::json;
use serde_json::Value;
use sqlx::{prelude::FromRow, types::Json};
use std::collections::HashMap;
use std::env;

pub type SqlSpaceRecord = (String, i64, i64, i64, i64);

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MetricRecord {
    pub experiment_uid: String,
    pub name: String,
    pub value: f64,
    pub step: Option<i32>,
    pub timestamp: Option<i64>,
    pub created_at: Option<DateTime<Utc>>,
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
            experiment_uid: create_uuid7(),
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
            experiment_uid: create_uuid7(),
            name: CommonKwargs::Undefined.to_string(),
            value: Json(ParameterValue::Int(0)),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct VersionResult {
    pub created_at: DateTime<Utc>,
    pub name: String,
    pub space: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
}

impl VersionResult {
    pub fn to_version(&self) -> Result<Version, SqlError> {
        let mut version = Version::new(self.major as u64, self.minor as u64, self.patch as u64);

        if self.pre_tag.is_some() {
            version.pre = Prerelease::new(self.pre_tag.as_ref().unwrap())
                .map_err(VersionError::InvalidVersion)?;
        }

        if self.build_tag.is_some() {
            version.build = BuildMetadata::new(self.build_tag.as_ref().unwrap())
                .map_err(VersionError::InvalidVersion)?;
        }

        Ok(version)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Space {
    pub space: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct QueryStats {
    pub nbr_names: i32,
    pub nbr_spaces: i32,
    pub nbr_versions: i32,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct CardSummary {
    pub space: String,
    pub name: String,
    pub version: String,
    pub versions: i64,
    pub updated_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub row_num: i64,
}

#[derive(Debug, FromRow, Serialize, Deserialize)]
pub struct VersionSummary {
    pub space: String,
    pub name: String,
    pub version: String,
    pub created_at: DateTime<Utc>,
    pub row_num: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct DataCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
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
    pub opsml_version: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl DataCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        tags: Vec<String>,
        data_type: String,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        interface_type: String,
        username: String,
        opsml_version: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        DataCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
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
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Data,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: DataCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;
        Ok(DataCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            tags: Json(client_card.tags),
            data_type: client_card.data_type,
            experimentcard_uid: client_card.experimentcard_uid,
            auditcard_uid: client_card.auditcard_uid,
            interface_type: client_card.interface_type,
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

impl Default for DataCardRecord {
    fn default() -> Self {
        DataCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
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
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ModelCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
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
    pub opsml_version: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl ModelCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        tags: Vec<String>,
        datacard_uid: Option<String>,
        data_type: String,
        model_type: String,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        interface_type: String,
        task_type: String,
        opsml_version: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        ModelCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
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
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Model,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: ModelCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

        Ok(ModelCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            tags: Json(client_card.tags),
            datacard_uid: client_card.datacard_uid,
            data_type: client_card.data_type,
            model_type: client_card.model_type,
            experimentcard_uid: client_card.experimentcard_uid,
            auditcard_uid: client_card.auditcard_uid,
            interface_type: client_card.interface_type,
            task_type: client_card.task_type,
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

impl Default for ModelCardRecord {
    fn default() -> Self {
        ModelCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
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
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExperimentCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
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
    pub service_card_uids: Json<Vec<String>>,
    pub experimentcard_uids: Json<Vec<String>>,
    pub opsml_version: String,
    pub username: String,
}

impl Default for ExperimentCardRecord {
    fn default() -> Self {
        ExperimentCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
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
            service_card_uids: Json(Vec::new()),
            experimentcard_uids: Json(Vec::new()),
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[allow(clippy::too_many_arguments)]
impl ExperimentCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        tags: Vec<String>,
        datacard_uids: Vec<String>,
        modelcard_uids: Vec<String>,
        promptcard_uids: Vec<String>,
        service_card_uids: Vec<String>,
        experimentcard_uids: Vec<String>,
        opsml_version: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        ExperimentCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
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
            service_card_uids: Json(service_card_uids),
            experimentcard_uids: Json(experimentcard_uids),
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Experiment,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: ExperimentCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

        Ok(ExperimentCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            tags: Json(client_card.tags),
            datacard_uids: Json(client_card.datacard_uids),
            modelcard_uids: Json(client_card.modelcard_uids),
            promptcard_uids: Json(client_card.promptcard_uids),
            service_card_uids: Json(client_card.service_card_uids),
            experimentcard_uids: Json(client_card.experimentcard_uids),
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AuditCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
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
    pub opsml_version: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl AuditCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        tags: Vec<String>,
        approved: bool,
        datacard_uids: Vec<String>,
        modelcard_uids: Vec<String>,
        experimentcard_uids: Vec<String>,
        opsml_version: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        AuditCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
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
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Audit,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: AuditCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;
        Ok(AuditCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            tags: Json(client_card.tags),
            approved: client_card.approved,
            datacard_uids: Json(client_card.datacard_uids),
            modelcard_uids: Json(client_card.modelcard_uids),
            experimentcard_uids: Json(client_card.experimentcard_uids),
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

impl Default for AuditCardRecord {
    fn default() -> Self {
        AuditCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
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
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct PromptCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub name: String,
    pub space: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub version: String,
    pub tags: Json<Vec<String>>,
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,
    pub opsml_version: String,
    pub username: String,
}

#[allow(clippy::too_many_arguments)]
impl PromptCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        tags: Vec<String>,
        experimentcard_uid: Option<String>,
        auditcard_uid: Option<String>,
        opsml_version: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        PromptCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            tags: Json(tags),
            experimentcard_uid,
            auditcard_uid,
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Prompt,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: PromptCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

        Ok(PromptCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            tags: Json(client_card.tags),
            experimentcard_uid: client_card.experimentcard_uid,
            auditcard_uid: client_card.auditcard_uid,
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

impl Default for PromptCardRecord {
    fn default() -> Self {
        PromptCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            tags: Json(Vec::new()),
            experimentcard_uid: None,
            auditcard_uid: None,
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ServiceCardRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub space: String,
    pub name: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub version: String,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub cards: Json<Vec<CardEntry>>,
    pub opsml_version: String,
    pub username: String,
}

impl ServiceCardRecord {
    pub fn new(
        name: String,
        space: String,
        version: Version,
        cards: Vec<CardEntry>,
        opsml_version: String,
        username: String,
    ) -> Self {
        let created_at = get_utc_datetime();
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        ServiceCardRecord {
            uid,
            created_at,
            app_env,
            name,
            space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            cards: Json(cards),
            opsml_version,
            username,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Service,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn from_client_card(client_card: ServiceCardClientRecord) -> Result<Self, SqlError> {
        let version = Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

        Ok(ServiceCardRecord {
            uid: client_card.uid,
            created_at: client_card.created_at,
            app_env: client_card.app_env,
            name: client_card.name,
            space: client_card.space,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: Some(version.pre.to_string()),
            build_tag: Some(version.build.to_string()),
            version: client_card.version,
            cards: Json(client_card.cards),
            opsml_version: client_card.opsml_version,
            username: client_card.username,
        })
    }
}

impl Default for ServiceCardRecord {
    fn default() -> Self {
        ServiceCardRecord {
            uid: create_uuid7(),
            created_at: get_utc_datetime(),
            app_env: env::var("APP_ENV").unwrap_or_else(|_| "development".to_string()),
            name: CommonKwargs::Undefined.to_string(),
            space: CommonKwargs::Undefined.to_string(),
            major: 1,
            minor: 0,
            patch: 0,
            pre_tag: None,
            build_tag: None,
            version: Version::new(1, 0, 0).to_string(),
            cards: Json(Vec::new()),
            opsml_version: opsml_version::version(),
            username: CommonKwargs::Undefined.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ArtifactSqlRecord {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub space: String,
    pub name: String,
    pub major: i32,
    pub minor: i32,
    pub patch: i32,
    pub version: String,
    pub pre_tag: Option<String>,
    pub build_tag: Option<String>,
    pub media_type: String,
    pub updated_at: DateTime<Utc>,
}

impl ArtifactSqlRecord {
    pub fn new(space: String, name: String, version: Version, media_type: String) -> Self {
        let created_at = get_utc_datetime();
        let updated_at = created_at;
        let app_env = env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
        let uid = create_uuid7();

        ArtifactSqlRecord {
            uid,
            created_at,
            app_env,
            space,
            name,
            major: version.major as i32,
            minor: version.minor as i32,
            patch: version.patch as i32,
            pre_tag: version.pre.to_string().parse().ok(),
            build_tag: version.build.to_string().parse().ok(),
            version: version.to_string(),
            media_type,
            updated_at,
        }
    }

    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Artifact,
            self.space,
            self.name,
            self.version
        )
    }

    pub fn get_metadata(&self) -> String {
        let metadata = json!({
            "uid": self.uid,
            "created_at": self.created_at,
            "app_env": self.app_env,
            "space": self.space,
            "filename": self.name,
            "version": self.version,
            "media_type": self.media_type,
        });
        metadata.to_string()
    }

    pub fn to_artifact_record(&self) -> ArtifactRecord {
        ArtifactRecord {
            uid: self.uid.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            media_type: self.media_type.clone(),
            created_at: self.created_at,
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
    Service(Vec<ServiceCardRecord>),
}

impl CardResults {
    pub fn len(&self) -> usize {
        match self {
            CardResults::Data(cards) => cards.len(),
            CardResults::Model(cards) => cards.len(),
            CardResults::Experiment(cards) => cards.len(),
            CardResults::Audit(cards) => cards.len(),
            CardResults::Prompt(cards) => cards.len(),
            CardResults::Service(cards) => cards.len(),
        }
    }
    pub fn is_empty(&self) -> bool {
        match self {
            CardResults::Data(cards) => cards.is_empty(),
            CardResults::Model(cards) => cards.is_empty(),
            CardResults::Experiment(cards) => cards.is_empty(),
            CardResults::Audit(cards) => cards.is_empty(),
            CardResults::Prompt(cards) => cards.is_empty(),
            CardResults::Service(cards) => cards.is_empty(),
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
            CardResults::Service(cards) => cards
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
    Service(ServiceCardRecord),
}

impl ServerCard {
    pub fn uid(&self) -> &str {
        match self {
            ServerCard::Data(card) => card.uid.as_str(),
            ServerCard::Model(card) => card.uid.as_str(),
            ServerCard::Experiment(card) => card.uid.as_str(),
            ServerCard::Audit(card) => card.uid.as_str(),
            ServerCard::Prompt(card) => card.uid.as_str(),
            ServerCard::Service(card) => card.uid.as_str(),
        }
    }

    pub fn registry_type(&self) -> String {
        match self {
            ServerCard::Data(_) => RegistryType::Data.to_string(),
            ServerCard::Model(_) => RegistryType::Model.to_string(),
            ServerCard::Experiment(_) => RegistryType::Experiment.to_string(),
            ServerCard::Audit(_) => RegistryType::Audit.to_string(),
            ServerCard::Prompt(_) => RegistryType::Prompt.to_string(),
            ServerCard::Service(_) => RegistryType::Service.to_string(),
        }
    }

    pub fn version(&self) -> String {
        match self {
            ServerCard::Data(card) => card.version.clone(),
            ServerCard::Model(card) => card.version.clone(),
            ServerCard::Experiment(card) => card.version.clone(),
            ServerCard::Audit(card) => card.version.clone(),
            ServerCard::Prompt(card) => card.version.clone(),
            ServerCard::Service(card) => card.version.clone(),
        }
    }

    pub fn space(&self) -> String {
        match self {
            ServerCard::Data(card) => card.space.clone(),
            ServerCard::Model(card) => card.space.clone(),
            ServerCard::Experiment(card) => card.space.clone(),
            ServerCard::Audit(card) => card.space.clone(),
            ServerCard::Prompt(card) => card.space.clone(),
            ServerCard::Service(card) => card.space.clone(),
        }
    }

    pub fn name(&self) -> String {
        match self {
            ServerCard::Data(card) => card.name.clone(),
            ServerCard::Model(card) => card.name.clone(),
            ServerCard::Experiment(card) => card.name.clone(),
            ServerCard::Audit(card) => card.name.clone(),
            ServerCard::Prompt(card) => card.name.clone(),
            ServerCard::Service(card) => card.name.clone(),
        }
    }

    pub fn uri(&self) -> String {
        match self {
            ServerCard::Data(card) => card.uri(),
            ServerCard::Model(card) => card.uri(),
            ServerCard::Experiment(card) => card.uri(),
            ServerCard::Audit(card) => card.uri(),
            ServerCard::Prompt(card) => card.uri(),
            ServerCard::Service(card) => card.uri(),
        }
    }

    pub fn app_env(&self) -> String {
        match self {
            ServerCard::Data(card) => card.app_env.clone(),
            ServerCard::Model(card) => card.app_env.clone(),
            ServerCard::Experiment(card) => card.app_env.clone(),
            ServerCard::Audit(card) => card.app_env.clone(),
            ServerCard::Prompt(card) => card.app_env.clone(),
            ServerCard::Service(card) => card.app_env.clone(),
        }
    }

    pub fn created_at(&self) -> DateTime<Utc> {
        match self {
            ServerCard::Data(card) => card.created_at,
            ServerCard::Model(card) => card.created_at,
            ServerCard::Experiment(card) => card.created_at,
            ServerCard::Audit(card) => card.created_at,
            ServerCard::Prompt(card) => card.created_at,
            ServerCard::Service(card) => card.created_at,
        }
    }

    /// Convert a `Card` enum to a `ServerCard` enum.
    ///
    /// # Arguments
    /// * `card` - A `Card` enum variant.
    pub fn from_card(card: CardRecord) -> Result<Self, SqlError> {
        match card {
            CardRecord::Data(card) => Ok(ServerCard::Data(DataCardRecord::from_client_card(card)?)),
            CardRecord::Model(card) => {
                Ok(ServerCard::Model(ModelCardRecord::from_client_card(card)?))
            }
            CardRecord::Experiment(card) => Ok(ServerCard::Experiment(
                ExperimentCardRecord::from_client_card(card)?,
            )),
            CardRecord::Audit(card) => {
                Ok(ServerCard::Audit(AuditCardRecord::from_client_card(card)?))
            }
            CardRecord::Prompt(card) => Ok(ServerCard::Prompt(PromptCardRecord::from_client_card(
                card,
            )?)),
            CardRecord::Service(card) => Ok(ServerCard::Service(
                ServiceCardRecord::from_client_card(card)?,
            )),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HardwareMetricsRecord {
    pub experiment_uid: String,
    pub created_at: DateTime<Utc>,
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
            experiment_uid: create_uuid7(),
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

#[derive(Serialize, Deserialize, Clone, Default)]
pub struct User {
    pub id: Option<i32>,
    pub created_at: DateTime<Utc>,
    pub active: bool,
    pub username: String,
    pub password_hash: String,
    pub hashed_recovery_codes: Vec<String>,
    pub permissions: Vec<String>,
    pub group_permissions: Vec<String>,
    pub role: String,
    pub favorite_spaces: Vec<String>,
    pub refresh_token: Option<String>,
    pub email: String,
    pub updated_at: DateTime<Utc>,
    pub authentication_type: String,
}

impl User {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        username: String,
        password_hash: String,
        email: String,
        hashed_recovery_codes: Vec<String>,
        permissions: Option<Vec<String>>,
        group_permissions: Option<Vec<String>>,
        role: Option<String>,
        favorite_spaces: Option<Vec<String>>,
        authentication_type: Option<String>,
    ) -> Self {
        let created_at = get_utc_datetime();

        User {
            id: None,
            created_at,
            active: true,
            username,
            password_hash,
            hashed_recovery_codes,
            permissions: permissions.unwrap_or(vec!["read:all".to_string()]),
            group_permissions: group_permissions.unwrap_or(vec!["user".to_string()]),
            favorite_spaces: favorite_spaces.unwrap_or_default(),
            role: role.unwrap_or("user".to_string()),
            refresh_token: None,
            email,
            updated_at: created_at,
            authentication_type: authentication_type.unwrap_or("basic".to_string()),
        }
    }

    /// Convenience constructor for creating a new user from SSO (Single Sign-On) data.
    pub fn new_from_sso(username: &str, email: &str) -> Self {
        let created_at = get_utc_datetime();

        User {
            id: None,
            created_at,
            active: true,
            username: username.to_string(),
            password_hash: "[redacted]".to_string(),
            hashed_recovery_codes: Vec::new(),
            permissions: vec!["read:all".to_string(), "write:all".to_string()],
            group_permissions: vec!["user".to_string()],
            favorite_spaces: Vec::new(),
            role: "user".to_string(),
            refresh_token: None,
            email: email.to_string(),
            updated_at: created_at,
            authentication_type: "sso".to_string(),
        }
    }

    pub fn serialize(&self) -> String {
        // convert to HashMap<String, Value>
        // redact password_hash and permissions
        let mut map: HashMap<String, Value> = HashMap::new();
        map.insert("id".to_string(), self.id.into());
        map.insert("created_at".to_string(), self.created_at.to_string().into());
        map.insert("active".to_string(), self.active.into());
        map.insert("username".to_string(), self.username.clone().into());
        map.insert("email".to_string(), self.email.clone().into());
        map.insert("password_hash".to_string(), "[redacted]".into());
        map.insert("hashed_recovery_codes".to_string(), "[redacted]".into());
        map.insert("permissions".to_string(), self.permissions.clone().into());
        map.insert(
            "group_permissions".to_string(),
            self.group_permissions.clone().into(),
        );
        map.insert("role".to_string(), self.role.clone().into());
        map.insert(
            "favorite_spaces".to_string(),
            self.favorite_spaces.clone().into(),
        );
        map.insert("refresh_token".to_string(), "[redacted]".into());
        map.insert("updated_at".to_string(), self.updated_at.to_string().into());
        map.insert(
            "authentication_type".to_string(),
            self.authentication_type.clone().into(),
        );

        // convert to JSON
        serde_json::to_string(&map).unwrap_or_else(|_| "{}".to_string())
    }
}

impl std::fmt::Debug for User {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("User")
            .field("id", &self.id)
            .field("username", &self.username)
            .field("email", &self.email)
            .field("active", &self.active)
            .field("password_hash", &"[redacted]")
            .field("hashed_recovery_codes", &"[redacted]")
            .field("permissions", &"[redacted]")
            .field("group_permissions", &self.group_permissions)
            .field("role", &self.role)
            .field("favorite_spaces", &self.favorite_spaces)
            .field("created_at", &self.created_at)
            .field("updated_at", &self.updated_at)
            .field("authentication_type", &self.authentication_type)
            .finish()
    }
}
