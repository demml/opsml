use crate::error::SqlError;
use crate::schemas::schema::{
    ArtifactSqlRecord, AuditCardRecord, CardResults, CardSummary, DataCardRecord,
    ExperimentCardRecord, HardwareMetricsRecord, MetricRecord, ModelCardRecord, ParameterRecord,
    PromptCardRecord, QueryStats, ServerCard, ServiceCardRecord, SqlSpaceRecord, User,
    VersionResult, VersionSummary,
};
use async_trait::async_trait;
use opsml_types::cards::CardTable;

use opsml_types::contracts::CardQueryArgs;
use sqlx::{Database, Pool};

#[async_trait]
pub trait CardLogicTrait {
    async fn check_uid_exists(&self, uid: &str, table: &CardTable) -> Result<bool, SqlError>;
    async fn get_versions(
        &self,
        table: &CardTable,
        space: &str,
        name: &str,
        version: Option<String>,
    ) -> Result<Vec<String>, SqlError>;
    async fn query_cards(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<CardResults, SqlError>;
    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError>;
    async fn update_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError>;
    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
        space: Option<&str>,
    ) -> Result<QueryStats, SqlError>;
    async fn query_page(
        &self,
        sort_by: &str,
        page: i32,
        search_term: Option<&str>,
        space: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError>;
    async fn version_page(
        &self,
        page: i32,
        space: Option<&str>,
        name: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError>;
    async fn delete_card(&self, table: &CardTable, uid: &str)
        -> Result<(String, String), SqlError>;
    async fn get_unique_space_names(&self, table: &CardTable) -> Result<Vec<String>, SqlError>;
}

#[async_trait]
pub trait ExperimentLogicTrait {
    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError>;
    async fn insert_experiment_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError>;
    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
        is_eval: Option<bool>,
    ) -> Result<Vec<MetricRecord>, SqlError>;
    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError>;
    async fn insert_hardware_metrics(&self, record: &HardwareMetricsRecord)
        -> Result<(), SqlError>;
    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError>;
    async fn insert_experiment_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError>;
    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError>;
}
