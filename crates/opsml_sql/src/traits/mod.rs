use crate::error::SqlError;
use crate::schemas::schema::{
    ArtifactSqlRecord, CardResults, CardSummary, HardwareMetricsRecord, MetricRecord,
    ParameterRecord, QueryStats, ServerCard, User, VersionSummary,
};
use crate::schemas::{EvaluationSqlRecord, ServiceCardRecord};
use async_trait::async_trait;
use opsml_types::cards::CardTable;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::{
    RegistryType,
    contracts::{
        ArtifactKey, ArtifactQueryArgs, ArtifactRecord, AuditEvent, CardArgs, DashboardStats,
        ServiceQueryArgs, SpaceNameEvent, SpaceRecord, SpaceStats, VersionCursor,
    },
};

#[async_trait]
pub trait CardLogicTrait {
    async fn compare_hash(
        &self,
        table: &CardTable,
        content_hash: &[u8],
    ) -> Result<Option<CardArgs>, SqlError>;
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
        spaces: &[String],
        tags: &[String],
    ) -> Result<QueryStats, SqlError>;
    async fn query_dashboard_stats(&self) -> Result<DashboardStats, SqlError>;

    #[allow(clippy::too_many_arguments)]
    async fn query_page(
        &self,
        sort_by: &str,
        limit: i32,
        offset: i32,
        search_term: Option<&str>,
        spaces: &[String],
        tags: &[String],
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError>;
    async fn version_page(
        &self,
        cursor: &VersionCursor,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError>;
    async fn delete_card(&self, table: &CardTable, uid: &str)
    -> Result<(String, String), SqlError>;
    async fn get_unique_space_names(&self, table: &CardTable) -> Result<Vec<String>, SqlError>;
    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError>;

    async fn get_recent_services(
        &self,
        query_args: &ServiceQueryArgs,
    ) -> Result<Vec<ServiceCardRecord>, SqlError>;

    async fn get_unique_tags(&self, table: &CardTable) -> Result<Vec<String>, SqlError>;
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

#[async_trait]
pub trait UserLogicTrait {
    async fn insert_user(&self, user: &User) -> Result<(), SqlError>;
    async fn get_user(
        &self,
        username: &str,
        auth_type: Option<&str>,
    ) -> Result<Option<User>, SqlError>;
    async fn get_users(&self) -> Result<Vec<User>, SqlError>;
    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError>;
    async fn delete_user(&self, username: &str) -> Result<(), SqlError>;
    async fn update_user(&self, user: &User) -> Result<(), SqlError>;
}

#[async_trait]
pub trait ArtifactLogicTrait {
    async fn insert_artifact_record(&self, record: &ArtifactSqlRecord) -> Result<(), SqlError>;
    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError>;
    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError>;
    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError>;
    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError>;
    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError>;
    async fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, SqlError>;
}

#[async_trait]
pub trait SpaceLogicTrait {
    async fn insert_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError>;
    async fn insert_space_name_record(&self, event: &SpaceNameEvent) -> Result<(), SqlError>;
    async fn get_all_space_stats(&self) -> Result<Vec<SpaceStats>, SqlError>;
    async fn get_space_record(&self, space: &str) -> Result<Option<SpaceRecord>, SqlError>;
    async fn update_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError>;
    async fn delete_space_record(&self, space: &str) -> Result<(), SqlError>;
    async fn delete_space_name_record(
        &self,
        space: &str,
        name: &str,
        registry_type: &RegistryType,
    ) -> Result<(), SqlError>;
}

#[async_trait]
pub trait AuditLogicTrait {
    async fn insert_audit_event(&self, event: AuditEvent) -> Result<(), SqlError>;
}

#[async_trait]
pub trait EvaluationLogicTrait {
    async fn insert_evaluation_record(&self, event: EvaluationSqlRecord) -> Result<(), SqlError>;

    async fn get_evaluation_record(&self, uid: &str) -> Result<EvaluationSqlRecord, SqlError>;
}
