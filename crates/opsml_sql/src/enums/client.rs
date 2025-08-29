use crate::base::SqlClient;
use crate::error::SqlError;
use crate::mysql::client::MySqlClient;
use crate::postgres::client::PostgresClient;
use crate::schemas::schema::{
    ArtifactSqlRecord, CardResults, CardSummary, HardwareMetricsRecord, MetricRecord,
    ParameterRecord, QueryStats, ServerCard, User,
};
use crate::schemas::VersionSummary;
use crate::sqlite::client::SqliteClient;
use anyhow::Context;
use anyhow::Result as AnyhowResult;
use async_trait::async_trait;
use opsml_settings::config::DatabaseSettings;
use opsml_types::contracts::{
    ArtifactQueryArgs, ArtifactRecord, AuditEvent, SpaceNameEvent, SpaceRecord, SpaceStats,
};
use opsml_types::{
    RegistryType, SqlType,
    {
        cards::CardTable,
        contracts::{ArtifactKey, CardQueryArgs},
    },
};
use tracing::debug;

#[derive(Debug, Clone)]
pub enum SqlClientEnum {
    Postgres(PostgresClient),
    Sqlite(SqliteClient),
    MySql(MySqlClient),
}

impl SqlClientEnum {
    pub fn name(&self) -> String {
        match self {
            SqlClientEnum::Postgres(_) => "Postgres".to_string(),
            SqlClientEnum::Sqlite(_) => "Sqlite".to_string(),
            SqlClientEnum::MySql(_) => "MySql".to_string(),
        }
    }
    pub async fn query(&self, sql: &str) {
        match self {
            SqlClientEnum::Postgres(client) => {
                sqlx::query(sql).execute(&client.pool).await.unwrap();
            }
            SqlClientEnum::Sqlite(client) => {
                sqlx::query(sql).execute(&client.pool).await.unwrap();
            }
            SqlClientEnum::MySql(client) => {
                sqlx::query(sql).execute(&client.pool).await.unwrap();
            }
        }
    }
}

#[async_trait]
impl SqlClient for SqlClientEnum {
    async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        match settings.sql_type {
            SqlType::Postgres => {
                let client = PostgresClient::new(settings).await?;
                Ok(SqlClientEnum::Postgres(client))
            }
            SqlType::Sqlite => {
                let client = SqliteClient::new(settings).await?;
                Ok(SqlClientEnum::Sqlite(client))
            }
            SqlType::MySql => {
                let client = MySqlClient::new(settings).await?;
                Ok(SqlClientEnum::MySql(client))
            }
        }
    }

    async fn check_uid_exists(&self, uid: &str, table: &CardTable) -> Result<bool, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.check_uid_exists(uid, table).await,
            SqlClientEnum::Sqlite(client) => client.check_uid_exists(uid, table).await,
            SqlClientEnum::MySql(client) => client.check_uid_exists(uid, table).await,
        }
    }

    async fn insert_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_card(table, card).await,
            SqlClientEnum::Sqlite(client) => client.insert_card(table, card).await,
            SqlClientEnum::MySql(client) => client.insert_card(table, card).await,
        }
    }

    async fn insert_artifact_record(&self, record: &ArtifactSqlRecord) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_artifact_record(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_artifact_record(record).await,
            SqlClientEnum::MySql(client) => client.insert_artifact_record(record).await,
        }
    }

    async fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.query_artifacts(query_args).await,
            SqlClientEnum::Sqlite(client) => client.query_artifacts(query_args).await,
            SqlClientEnum::MySql(client) => client.query_artifacts(query_args).await,
        }
    }

    async fn update_card(&self, table: &CardTable, card: &ServerCard) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_card(table, card).await,
            SqlClientEnum::Sqlite(client) => client.update_card(table, card).await,
            SqlClientEnum::MySql(client) => client.update_card(table, card).await,
        }
    }

    async fn query_stats(
        &self,
        table: &CardTable,
        search_term: Option<&str>,
        space: Option<&str>,
    ) -> Result<QueryStats, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.query_stats(table, search_term, space).await,
            SqlClientEnum::Sqlite(client) => client.query_stats(table, search_term, space).await,
            SqlClientEnum::MySql(client) => client.query_stats(table, search_term, space).await,
        }
    }

    async fn query_page(
        &self,
        sort_by: &str,
        page: i32,
        search_term: Option<&str>,
        space: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<CardSummary>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client
                    .query_page(sort_by, page, search_term, space, table)
                    .await
            }
            SqlClientEnum::Sqlite(client) => {
                client
                    .query_page(sort_by, page, search_term, space, table)
                    .await
            }
            SqlClientEnum::MySql(client) => {
                client
                    .query_page(sort_by, page, search_term, space, table)
                    .await
            }
        }
    }

    async fn version_page(
        &self,
        page: i32,
        space: Option<&str>,
        name: Option<&str>,
        table: &CardTable,
    ) -> Result<Vec<VersionSummary>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.version_page(page, space, name, table).await,
            SqlClientEnum::Sqlite(client) => client.version_page(page, space, name, table).await,
            SqlClientEnum::MySql(client) => client.version_page(page, space, name, table).await,
        }
    }

    async fn delete_card(
        &self,
        table: &CardTable,
        uid: &str,
    ) -> Result<(String, String), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.delete_card(table, uid).await,
            SqlClientEnum::Sqlite(client) => client.delete_card(table, uid).await,
            SqlClientEnum::MySql(client) => client.delete_card(table, uid).await,
        }
    }

    async fn query_cards(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<CardResults, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.query_cards(table, query_args).await,
            SqlClientEnum::Sqlite(client) => client.query_cards(table, query_args).await,
            SqlClientEnum::MySql(client) => client.query_cards(table, query_args).await,
        }
    }
    async fn run_migrations(&self) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.run_migrations().await,
            SqlClientEnum::Sqlite(client) => client.run_migrations().await,
            SqlClientEnum::MySql(client) => client.run_migrations().await,
        }
    }

    async fn get_unique_space_names(&self, table: &CardTable) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_unique_space_names(table).await,
            SqlClientEnum::Sqlite(client) => client.get_unique_space_names(table).await,
            SqlClientEnum::MySql(client) => client.get_unique_space_names(table).await,
        }
    }

    async fn get_versions(
        &self,
        table: &CardTable,
        space: &str,
        name: &str,
        version: Option<String>,
    ) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client.get_versions(table, space, name, version).await
            }
            SqlClientEnum::Sqlite(client) => client.get_versions(table, space, name, version).await,
            SqlClientEnum::MySql(client) => client.get_versions(table, space, name, version).await,
        }
    }

    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_experiment_metric(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_experiment_metric(record).await,
            SqlClientEnum::MySql(client) => client.insert_experiment_metric(record).await,
        }
    }

    async fn insert_experiment_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_experiment_metrics(records).await,
            SqlClientEnum::Sqlite(client) => client.insert_experiment_metrics(records).await,
            SqlClientEnum::MySql(client) => client.insert_experiment_metrics(records).await,
        }
    }

    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
        is_eval: Option<bool>,
    ) -> Result<Vec<MetricRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client.get_experiment_metric(uid, names, is_eval).await
            }
            SqlClientEnum::Sqlite(client) => {
                client.get_experiment_metric(uid, names, is_eval).await
            }
            SqlClientEnum::MySql(client) => client.get_experiment_metric(uid, names, is_eval).await,
        }
    }

    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_experiment_metric_names(uid).await,
            SqlClientEnum::Sqlite(client) => client.get_experiment_metric_names(uid).await,
            SqlClientEnum::MySql(client) => client.get_experiment_metric_names(uid).await,
        }
    }

    async fn insert_hardware_metrics(
        &self,
        record: &HardwareMetricsRecord,
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_hardware_metrics(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_hardware_metrics(record).await,
            SqlClientEnum::MySql(client) => client.insert_hardware_metrics(record).await,
        }
    }

    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_hardware_metric(uid).await,
            SqlClientEnum::Sqlite(client) => client.get_hardware_metric(uid).await,
            SqlClientEnum::MySql(client) => client.get_hardware_metric(uid).await,
        }
    }

    async fn insert_experiment_parameters<'life1>(
        &self,
        record: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_experiment_parameters(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_experiment_parameters(record).await,
            SqlClientEnum::MySql(client) => client.insert_experiment_parameters(record).await,
        }
    }

    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_experiment_parameter(uid, names).await,
            SqlClientEnum::Sqlite(client) => client.get_experiment_parameter(uid, names).await,
            SqlClientEnum::MySql(client) => client.get_experiment_parameter(uid, names).await,
        }
    }

    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_user(user).await,
            SqlClientEnum::Sqlite(client) => client.insert_user(user).await,
            SqlClientEnum::MySql(client) => client.insert_user(user).await,
        }
    }

    async fn get_user(
        &self,
        username: &str,
        auth_type: Option<&str>,
    ) -> Result<Option<User>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_user(username, auth_type).await,
            SqlClientEnum::Sqlite(client) => client.get_user(username, auth_type).await,
            SqlClientEnum::MySql(client) => client.get_user(username, auth_type).await,
        }
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_user(user).await,
            SqlClientEnum::Sqlite(client) => client.update_user(user).await,
            SqlClientEnum::MySql(client) => client.update_user(user).await,
        }
    }

    async fn get_users(&self) -> Result<Vec<User>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_users().await,
            SqlClientEnum::Sqlite(client) => client.get_users().await,
            SqlClientEnum::MySql(client) => client.get_users().await,
        }
    }

    async fn delete_user(&self, username: &str) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.delete_user(username).await,
            SqlClientEnum::Sqlite(client) => client.delete_user(username).await,
            SqlClientEnum::MySql(client) => client.delete_user(username).await,
        }
    }

    async fn is_last_admin(&self, username: &str) -> Result<bool, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.is_last_admin(username).await,
            SqlClientEnum::Sqlite(client) => client.is_last_admin(username).await,
            SqlClientEnum::MySql(client) => client.is_last_admin(username).await,
        }
    }

    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        debug!("Inserting artifact key");
        match self {
            SqlClientEnum::Postgres(client) => client.insert_artifact_key(key).await,
            SqlClientEnum::Sqlite(client) => client.insert_artifact_key(key).await,
            SqlClientEnum::MySql(client) => client.insert_artifact_key(key).await,
        }
    }

    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_artifact_key(uid, registry_type).await,
            SqlClientEnum::Sqlite(client) => client.get_artifact_key(uid, registry_type).await,
            SqlClientEnum::MySql(client) => client.get_artifact_key(uid, registry_type).await,
        }
    }

    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client
                    .get_artifact_key_from_path(storage_path, registry_type)
                    .await
            }
            SqlClientEnum::Sqlite(client) => {
                client
                    .get_artifact_key_from_path(storage_path, registry_type)
                    .await
            }
            SqlClientEnum::MySql(client) => {
                client
                    .get_artifact_key_from_path(storage_path, registry_type)
                    .await
            }
        }
    }

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_artifact_key(key).await,
            SqlClientEnum::Sqlite(client) => client.update_artifact_key(key).await,
            SqlClientEnum::MySql(client) => client.update_artifact_key(key).await,
        }
    }

    async fn insert_audit_event(&self, event: AuditEvent) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_audit_event(event).await,
            SqlClientEnum::Sqlite(client) => client.insert_audit_event(event).await,
            SqlClientEnum::MySql(client) => client.insert_audit_event(event).await,
        }
    }

    async fn get_card_key_for_loading(
        &self,
        table: &CardTable,
        query_args: &CardQueryArgs,
    ) -> Result<ArtifactKey, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client.get_card_key_for_loading(table, query_args).await
            }
            SqlClientEnum::Sqlite(client) => {
                client.get_card_key_for_loading(table, query_args).await
            }
            SqlClientEnum::MySql(client) => {
                client.get_card_key_for_loading(table, query_args).await
            }
        }
    }

    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.delete_artifact_key(uid, registry_type).await,
            SqlClientEnum::Sqlite(client) => client.delete_artifact_key(uid, registry_type).await,
            SqlClientEnum::MySql(client) => client.delete_artifact_key(uid, registry_type).await,
        }
    }

    async fn insert_space_record(&self, record: &SpaceRecord) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_space_record(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_space_record(record).await,
            SqlClientEnum::MySql(client) => client.insert_space_record(record).await,
        }
    }

    async fn insert_space_name_record(&self, event: &SpaceNameEvent) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_space_name_record(event).await,
            SqlClientEnum::Sqlite(client) => client.insert_space_name_record(event).await,
            SqlClientEnum::MySql(client) => client.insert_space_name_record(event).await,
        }
    }

    async fn get_all_space_stats(&self) -> Result<Vec<SpaceStats>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_all_space_stats().await,
            SqlClientEnum::Sqlite(client) => client.get_all_space_stats().await,
            SqlClientEnum::MySql(client) => client.get_all_space_stats().await,
        }
    }

    async fn get_space_record(&self, space: &str) -> Result<Option<SpaceRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_space_record(space).await,
            SqlClientEnum::Sqlite(client) => client.get_space_record(space).await,
            SqlClientEnum::MySql(client) => client.get_space_record(space).await,
        }
    }

    async fn update_space_record(&self, record: &SpaceRecord) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_space_record(record).await,
            SqlClientEnum::Sqlite(client) => client.update_space_record(record).await,
            SqlClientEnum::MySql(client) => client.update_space_record(record).await,
        }
    }

    async fn delete_space_record(&self, space: &str) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.delete_space_record(space).await,
            SqlClientEnum::Sqlite(client) => client.delete_space_record(space).await,
            SqlClientEnum::MySql(client) => client.delete_space_record(space).await,
        }
    }

    async fn delete_space_name_record(
        &self,
        space: &str,
        name: &str,
        registry_type: &RegistryType,
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client
                    .delete_space_name_record(space, name, registry_type)
                    .await
            }
            SqlClientEnum::Sqlite(client) => {
                client
                    .delete_space_name_record(space, name, registry_type)
                    .await
            }
            SqlClientEnum::MySql(client) => {
                client
                    .delete_space_name_record(space, name, registry_type)
                    .await
            }
        }
    }
}

pub async fn get_sql_client(db_settings: &DatabaseSettings) -> AnyhowResult<SqlClientEnum> {
    SqlClientEnum::new(db_settings).await.with_context(|| {
        format!(
            "Failed to create sql client for sql type: {:?}",
            db_settings.sql_type
        )
    })
}

#[cfg(test)]
mod tests {

    use super::*;
    use crate::schemas::schema::{
        AuditCardRecord, DataCardRecord, ExperimentCardRecord, ModelCardRecord,
    };
    use opsml_types::{CommonKwargs, RegistryType};
    use opsml_utils::utils::get_utc_datetime;

    use std::env;

    fn get_connection_uri() -> String {
        let mut current_dir = env::current_dir().expect("Failed to get current directory");
        current_dir.push("test.db");
        format!(
            "sqlite://{}",
            current_dir
                .to_str()
                .expect("Failed to convert path to string")
        )
    }

    pub fn cleanup() {
        // delete ./test.db if exists
        let mut current_dir = env::current_dir().expect("Failed to get current directory");
        current_dir.push("test.db");
        let _ = std::fs::remove_file(current_dir);
    }

    pub async fn get_client() -> SqlClientEnum {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqlClientEnum::new(&config).await.unwrap();
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        client.query(&script).await;

        client
    }

    #[tokio::test]
    async fn test_enum() {
        let _client = get_client().await;
    }

    // create test for non-memory sqlite

    #[tokio::test]
    async fn test_enum_versions() {
        let client = get_client().await;

        // query all versions
        // get versions (should return 1)
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", None)
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        // check star pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("1.*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("1.1.*".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        // check tilde pattern
        let versions = client
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1.1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("~1.1.1".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("^2.0.0".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_query_cards() {
        let client = get_client().await;

        // check if uid exists
        let exists = client
            .check_uid_exists("fake", &CardTable::Data)
            .await
            .unwrap();

        assert!(!exists);

        // try name and space
        let card_args = CardQueryArgs {
            name: Some("Data1".to_string()),
            space: Some("repo1".to_string()),
            ..Default::default()
        };

        // query all versions
        // get versions (should return 1)
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // try name and space
        let card_args = CardQueryArgs {
            name: Some("Model1".to_string()),
            space: Some("repo1".to_string()),
            version: Some("~1.0.0".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // max_date
        let card_args = CardQueryArgs {
            max_date: Some("2023-11-28".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Experiment, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        // try tags
        let tags = ["key1".to_string()].to_vec();
        let card_args = CardQueryArgs {
            tags: Some(tags),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        let card_args = CardQueryArgs {
            sort_by_timestamp: Some(true),
            limit: Some(5),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 5);

        // test uid
        let card_args = CardQueryArgs {
            uid: Some("550e8400-e29b-41d4-a716-446655440000".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check if uid exists
        let exists = client
            .check_uid_exists("550e8400-e29b-41d4-a716-446655440000", &CardTable::Data)
            .await
            .unwrap();

        assert!(exists);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_insert_cards() {
        let client = get_client().await;

        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert experimentcard
        let run_card = ExperimentCardRecord::default();
        let card = ServerCard::Experiment(run_card.clone());

        client
            .insert_card(&CardTable::Experiment, &card)
            .await
            .unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(run_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Experiment, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert auditcard

        let audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client.insert_card(&CardTable::Audit, &card).await.unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_update_cards() {
        let client = get_client().await;

        // Test DataCardRecord
        let mut data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        data_card.name = "UpdatedDataName".to_string();
        let updated_card = ServerCard::Data(data_card.clone());

        client
            .update_card(&CardTable::Data, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Data(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedDataName");
        }

        // Test ModelCardRecord
        let mut model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        model_card.name = "UpdatedModelName".to_string();
        let updated_card = ServerCard::Model(model_card.clone());

        client
            .update_card(&CardTable::Model, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Model(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedModelName");
        }

        // Test experimentcardRecord
        let mut run_card = ExperimentCardRecord::default();
        let card = ServerCard::Experiment(run_card.clone());

        client
            .insert_card(&CardTable::Experiment, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(run_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Experiment, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        run_card.name = "UpdatedRunName".to_string();
        let updated_card = ServerCard::Experiment(run_card.clone());

        client
            .update_card(&CardTable::Experiment, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Experiment, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Experiment(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedRunName");
        }

        // Test AuditCardRecord
        let mut audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client.insert_card(&CardTable::Audit, &card).await.unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        audit_card.name = "UpdatedAuditName".to_string();
        let updated_card = ServerCard::Audit(audit_card.clone());

        client
            .update_card(&CardTable::Audit, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardTable::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Audit(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedAuditName");
        }

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_unique_repos() {
        let client = get_client().await;

        // get unique space names
        let repos = client
            .get_unique_space_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 10);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_query_stats() {
        let client = get_client().await;
        // query stats
        let stats = client
            .query_stats(&CardTable::Model, None, None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 10);
        assert_eq!(stats.nbr_versions, 10);
        assert_eq!(stats.nbr_spaces, 10);

        // query stats with search term
        let stats = client
            .query_stats(&CardTable::Model, Some("Model1"), None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2); // for Model1 and Model10

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_query_page() {
        let client = get_client().await;

        // query page
        let results = client
            .query_page("name", 1, None, None, &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .query_page("name", 1, None, None, &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // query page
        let results = client
            .query_page("name", 1, None, Some("repo3"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        let results = client
            .version_page(1, Some("repo1"), Some("Model1"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_delete_card() {
        let client = get_client().await;

        // delete card

        let args = CardQueryArgs {
            uid: None,
            name: Some("Data1".to_string()),
            space: Some("repo1".to_string()),
            ..Default::default()
        };

        let cards = client.query_cards(&CardTable::Data, &args).await.unwrap();

        let uid = match cards {
            CardResults::Data(cards) => cards[0].uid.clone(),
            _ => "".to_string(),
        };

        assert!(!uid.is_empty());

        // delete the card
        client.delete_card(&CardTable::Data, &uid).await.unwrap();

        // check if the card was deleted
        let args = CardQueryArgs {
            uid: Some(uid),
            ..Default::default()
        };

        let results = client.query_cards(&CardTable::Data, &args).await.unwrap();

        assert_eq!(results.len(), 0);
    }

    // test run metric
    #[tokio::test]
    async fn test_enum_run_metric() {
        let client = get_client().await;

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let metric_names = vec!["metric1", "metric2", "metric3"];
        let eval_metric_names = vec!["eval_metric1", "eval_metric2"];

        for name in metric_names {
            let metric = MetricRecord {
                experiment_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                step: None,
                timestamp: None,
                created_at: None,
                idx: None,
                is_eval: false,
            };

            client.insert_experiment_metric(&metric).await.unwrap();
        }

        for name in eval_metric_names {
            let metric = MetricRecord {
                experiment_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                step: None,
                timestamp: None,
                created_at: None,
                idx: None,
                is_eval: true,
            };

            client.insert_experiment_metric(&metric).await.unwrap();
        }

        let records = client
            .get_experiment_metric(&uid, &Vec::new(), None)
            .await
            .unwrap();

        let names = client.get_experiment_metric_names(&uid).await.unwrap();

        assert_eq!(records.len(), 5);

        assert_eq!(names.len(), 5);

        let eval_records = client
            .get_experiment_metric(&uid, &Vec::new(), Some(true))
            .await
            .unwrap();

        assert_eq!(eval_records.len(), 2);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_hardware_metric() {
        let client = get_client().await;

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // create a loop of 10
        for _ in 0..10 {
            let metric = HardwareMetricsRecord {
                experiment_uid: uid.clone(),
                created_at: get_utc_datetime(),
                ..Default::default()
            };

            client.insert_hardware_metrics(&metric).await.unwrap();
        }

        let records = client.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 10);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_parameter() {
        let client = get_client().await;

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let parameter = ParameterRecord {
                experiment_uid: uid.clone(),
                name: format!("param{i}"),
                ..Default::default()
            };

            params.push(parameter);
        }

        client.insert_experiment_parameters(&params).await.unwrap();
        let records = client
            .get_experiment_parameter(&uid, &Vec::new())
            .await
            .unwrap();

        assert_eq!(records.len(), 10);

        let param_records = client
            .get_experiment_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(param_records.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_user() {
        let client = get_client().await;
        let recovery_codes = vec!["recovery_code_1".to_string(), "recovery_code_2".to_string()];

        let user = User::new(
            "user".to_string(),
            "pass".to_string(),
            "email".to_string(),
            recovery_codes,
            None,
            None,
            None,
            None,
            None,
        );
        let sso_user = User::new_from_sso("sso_user", "user@email.com");

        client.insert_user(&user).await.unwrap();
        client.insert_user(&sso_user).await.unwrap();

        let mut user = client.get_user("user", None).await.unwrap().unwrap();
        assert_eq!(user.username, "user");
        assert_eq!(user.email, "email");

        // update user
        user.active = false;

        client.update_user(&user).await.unwrap();
        let user = client.get_user("user", None).await.unwrap().unwrap();
        assert!(!user.active);

        // get all users
        let users = client.get_users().await.unwrap();
        assert_eq!(users.len(), 2);

        let user = client
            .get_user("sso_user", Some("sso"))
            .await
            .unwrap()
            .unwrap();
        assert!(user.active);

        // delete
        client.delete_user("sso_user").await.unwrap();

        // delete user
        client.delete_user("user").await.unwrap();

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_crud_space() {
        let client = get_client().await;

        // create a new space record
        let space_record = SpaceRecord {
            space: CommonKwargs::Undefined.to_string(),
            description: "Space description".to_string(),
        };

        client.insert_space_record(&space_record).await.unwrap();

        // insert datacard
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());
        client.insert_card(&CardTable::Data, &card).await.unwrap();

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());
        client.insert_card(&CardTable::Model, &card).await.unwrap();

        let space_event = SpaceNameEvent {
            space: data_card.space.clone(),
            name: data_card.name.clone(),
            registry_type: RegistryType::Data,
        };
        client.insert_space_name_record(&space_event).await.unwrap();

        let space_event = SpaceNameEvent {
            space: model_card.space.clone(),
            name: model_card.name.clone(),
            registry_type: RegistryType::Model,
        };

        client.insert_space_name_record(&space_event).await.unwrap();

        // get space stats
        let stats = client.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);
        // assert model_count
        assert_eq!(stats[0].model_count, 1);

        //create a new modelcard
        let model_card2 = ModelCardRecord {
            name: "Model2".to_string(),
            ..Default::default()
        };
        let card = ServerCard::Model(model_card2.clone());
        client.insert_card(&CardTable::Model, &card).await.unwrap();

        // update space stats again
        let space_event = SpaceNameEvent {
            space: model_card2.space.clone(),
            name: model_card2.name.clone(),
            registry_type: RegistryType::Model,
        };
        client.insert_space_name_record(&space_event).await.unwrap();
        // get space stats again

        let stats = client.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);

        // assert model_count
        assert_eq!(stats[0].model_count, 2);

        // update space record
        let updated_space_record = SpaceRecord {
            space: model_card2.space.clone(),
            description: "Updated Space description".to_string(),
        };
        client
            .update_space_record(&updated_space_record)
            .await
            .unwrap();

        // get space record
        let record = client
            .get_space_record(&model_card2.space)
            .await
            .unwrap()
            .unwrap();

        assert_eq!(record.description, "Updated Space description");

        // delete
        client
            .delete_space_record(&model_card2.space)
            .await
            .unwrap();

        // delete space name record
        client
            .delete_space_name_record(&model_card2.space, &model_card2.name, &RegistryType::Model)
            .await
            .unwrap();

        // get space stats again
        let stats = client.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);
        assert_eq!(stats[0].model_count, 1);

        cleanup();
    }
}
