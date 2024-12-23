use crate::base::SqlClient;
use crate::mysql::client::MySqlClient;
use crate::postgres::client::PostgresClient;
use crate::schemas::schema::{
    CardResults, CardSummary, HardwareMetricsRecord, MetricRecord, ParameterRecord, QueryStats,
    ServerCard, User,
};
use crate::sqlite::client::SqliteClient;
use anyhow::Context;
use anyhow::Result as AnyhowResult;
use async_trait::async_trait;
use opsml_error::error::SqlError;
use opsml_settings::config::{DatabaseSettings, OpsmlConfig};
use opsml_types::{CardQueryArgs, CardSQLTableNames, SqlType};

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

    async fn check_uid_exists(
        &self,
        uid: &str,
        table: &CardSQLTableNames,
    ) -> Result<bool, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.check_uid_exists(uid, table).await,
            SqlClientEnum::Sqlite(client) => client.check_uid_exists(uid, table).await,
            SqlClientEnum::MySql(client) => client.check_uid_exists(uid, table).await,
        }
    }

    async fn insert_card(
        &self,
        table: &CardSQLTableNames,
        card: &ServerCard,
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_card(table, card).await,
            SqlClientEnum::Sqlite(client) => client.insert_card(table, card).await,
            SqlClientEnum::MySql(client) => client.insert_card(table, card).await,
        }
    }

    async fn update_card(
        &self,
        table: &CardSQLTableNames,
        card: &ServerCard,
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_card(table, card).await,
            SqlClientEnum::Sqlite(client) => client.update_card(table, card).await,
            SqlClientEnum::MySql(client) => client.update_card(table, card).await,
        }
    }

    async fn query_stats(
        &self,
        table: &CardSQLTableNames,
        search_term: Option<&str>,
    ) -> Result<QueryStats, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.query_stats(table, search_term).await,
            SqlClientEnum::Sqlite(client) => client.query_stats(table, search_term).await,
            SqlClientEnum::MySql(client) => client.query_stats(table, search_term).await,
        }
    }

    async fn query_page(
        &self,
        sort_by: &str,
        page: i32,
        search_term: Option<&str>,
        repository: Option<&str>,
        table: &CardSQLTableNames,
    ) -> Result<Vec<CardSummary>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client
                    .query_page(sort_by, page, search_term, repository, table)
                    .await
            }
            SqlClientEnum::Sqlite(client) => {
                client
                    .query_page(sort_by, page, search_term, repository, table)
                    .await
            }
            SqlClientEnum::MySql(client) => {
                client
                    .query_page(sort_by, page, search_term, repository, table)
                    .await
            }
        }
    }

    async fn delete_card(&self, table: &CardSQLTableNames, uid: &str) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.delete_card(table, uid).await,
            SqlClientEnum::Sqlite(client) => client.delete_card(table, uid).await,
            SqlClientEnum::MySql(client) => client.delete_card(table, uid).await,
        }
    }

    async fn get_project_id(&self, project_name: &str, repository: &str) -> Result<i32, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client.get_project_id(project_name, repository).await
            }
            SqlClientEnum::Sqlite(client) => client.get_project_id(project_name, repository).await,
            SqlClientEnum::MySql(client) => client.get_project_id(project_name, repository).await,
        }
    }

    async fn query_cards(
        &self,
        table: &CardSQLTableNames,
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

    async fn get_unique_repository_names(
        &self,
        table: &CardSQLTableNames,
    ) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_unique_repository_names(table).await,
            SqlClientEnum::Sqlite(client) => client.get_unique_repository_names(table).await,
            SqlClientEnum::MySql(client) => client.get_unique_repository_names(table).await,
        }
    }

    async fn get_versions(
        &self,
        table: &CardSQLTableNames,
        name: &str,
        repository: &str,
        version: Option<&str>,
    ) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => {
                client.get_versions(table, name, repository, version).await
            }
            SqlClientEnum::Sqlite(client) => {
                client.get_versions(table, name, repository, version).await
            }
            SqlClientEnum::MySql(client) => {
                client.get_versions(table, name, repository, version).await
            }
        }
    }

    async fn insert_run_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_run_metric(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_run_metric(record).await,
            SqlClientEnum::MySql(client) => client.insert_run_metric(record).await,
        }
    }

    async fn insert_run_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_run_metrics(records).await,
            SqlClientEnum::Sqlite(client) => client.insert_run_metrics(records).await,
            SqlClientEnum::MySql(client) => client.insert_run_metrics(records).await,
        }
    }

    async fn get_run_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<MetricRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_run_metric(uid, names).await,
            SqlClientEnum::Sqlite(client) => client.get_run_metric(uid, names).await,
            SqlClientEnum::MySql(client) => client.get_run_metric(uid, names).await,
        }
    }

    async fn get_run_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_run_metric_names(uid).await,
            SqlClientEnum::Sqlite(client) => client.get_run_metric_names(uid).await,
            SqlClientEnum::MySql(client) => client.get_run_metric_names(uid).await,
        }
    }

    async fn insert_hardware_metrics<'life1>(
        &self,
        record: &'life1 [HardwareMetricsRecord],
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

    async fn insert_run_parameters<'life1>(
        &self,
        record: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_run_parameters(record).await,
            SqlClientEnum::Sqlite(client) => client.insert_run_parameters(record).await,
            SqlClientEnum::MySql(client) => client.insert_run_parameters(record).await,
        }
    }

    async fn get_run_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_run_parameter(uid, names).await,
            SqlClientEnum::Sqlite(client) => client.get_run_parameter(uid, names).await,
            SqlClientEnum::MySql(client) => client.get_run_parameter(uid, names).await,
        }
    }

    async fn insert_user(&self, user: &User) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.insert_user(user).await,
            SqlClientEnum::Sqlite(client) => client.insert_user(user).await,
            SqlClientEnum::MySql(client) => client.insert_user(user).await,
        }
    }

    async fn get_user(&self, username: &str) -> Result<User, SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.get_user(username).await,
            SqlClientEnum::Sqlite(client) => client.get_user(username).await,
            SqlClientEnum::MySql(client) => client.get_user(username).await,
        }
    }

    async fn update_user(&self, user: &User) -> Result<(), SqlError> {
        match self {
            SqlClientEnum::Postgres(client) => client.update_user(user).await,
            SqlClientEnum::Sqlite(client) => client.update_user(user).await,
            SqlClientEnum::MySql(client) => client.update_user(user).await,
        }
    }
}

pub async fn get_sql_client(config: &OpsmlConfig) -> AnyhowResult<SqlClientEnum> {
    let settings = &config.database_settings;
    SqlClientEnum::new(&config.database_settings)
        .await
        .with_context(|| {
            format!(
                "Failed to create sql client for sql type: {:?}",
                settings.sql_type
            )
        })
}

#[cfg(test)]
mod tests {

    use super::*;
    use crate::schemas::schema::{
        AuditCardRecord, DataCardRecord, ModelCardRecord, PipelineCardRecord, RunCardRecord,
    };
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
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", None)
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        // check star pattern
        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("1.*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("1.1.*"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("~1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        // check tilde pattern
        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("~1.1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("~1.1.1"))
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .get_versions(&CardSQLTableNames::Data, "Data1", "repo1", Some("^2.0.0"))
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
            .check_uid_exists("fake", &CardSQLTableNames::Data)
            .await
            .unwrap();

        assert!(!exists);

        // try name and repository
        let card_args = CardQueryArgs {
            name: Some("Data1".to_string()),
            repository: Some("repo1".to_string()),
            ..Default::default()
        };

        // query all versions
        // get versions (should return 1)
        let results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // try name and repository
        let card_args = CardQueryArgs {
            name: Some("Model1".to_string()),
            repository: Some("repo1".to_string()),
            version: Some("~1.0.0".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // max_date
        let card_args = CardQueryArgs {
            max_date: Some("2023-11-28".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        // try tags
        let tags = [("key1".to_string(), "value1".to_string())]
            .iter()
            .cloned()
            .collect();
        let card_args = CardQueryArgs {
            tags: Some(tags),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        let card_args = CardQueryArgs {
            sort_by_timestamp: Some(true),
            limit: Some(5),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 5);

        // test uid
        let card_args = CardQueryArgs {
            uid: Some("550e8400-e29b-41d4-a716-446655440000".to_string()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check if uid exists
        let exists = client
            .check_uid_exists(
                "550e8400-e29b-41d4-a716-446655440000",
                &CardSQLTableNames::Data,
            )
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

        client
            .insert_card(&CardSQLTableNames::Data, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client
            .insert_card(&CardSQLTableNames::Model, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardSQLTableNames::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert runcard
        let run_card = RunCardRecord::default();
        let card = ServerCard::Run(run_card.clone());

        client
            .insert_card(&CardSQLTableNames::Run, &card)
            .await
            .unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(run_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardSQLTableNames::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // insert auditcard

        let audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client
            .insert_card(&CardSQLTableNames::Audit, &card)
            .await
            .unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardSQLTableNames::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check pipeline card
        let pipeline_card = PipelineCardRecord::default();
        let card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .insert_card(&CardSQLTableNames::Pipeline, &card)
            .await
            .unwrap();

        // check if the card was inserted

        let card_args = CardQueryArgs {
            uid: Some(pipeline_card.uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardSQLTableNames::Pipeline, &card_args)
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

        client
            .insert_card(&CardSQLTableNames::Data, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(data_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        data_card.name = "UpdatedDataName".to_string();
        let updated_card = ServerCard::Data(data_card.clone());

        client
            .update_card(&CardSQLTableNames::Data, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardSQLTableNames::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Data(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedDataName");
        }

        // Test ModelCardRecord
        let mut model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());

        client
            .insert_card(&CardSQLTableNames::Model, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(model_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        model_card.name = "UpdatedModelName".to_string();
        let updated_card = ServerCard::Model(model_card.clone());

        client
            .update_card(&CardSQLTableNames::Model, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardSQLTableNames::Model, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Model(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedModelName");
        }

        // Test RunCardRecord
        let mut run_card = RunCardRecord::default();
        let card = ServerCard::Run(run_card.clone());

        client
            .insert_card(&CardSQLTableNames::Run, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(run_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        run_card.name = "UpdatedRunName".to_string();
        let updated_card = ServerCard::Run(run_card.clone());

        client
            .update_card(&CardSQLTableNames::Run, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardSQLTableNames::Run, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Run(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedRunName");
        }

        // Test AuditCardRecord
        let mut audit_card = AuditCardRecord::default();
        let card = ServerCard::Audit(audit_card.clone());

        client
            .insert_card(&CardSQLTableNames::Audit, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(audit_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        audit_card.name = "UpdatedAuditName".to_string();
        let updated_card = ServerCard::Audit(audit_card.clone());

        client
            .update_card(&CardSQLTableNames::Audit, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardSQLTableNames::Audit, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Audit(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedAuditName");
        }

        // Test PipelineCardRecord
        let mut pipeline_card = PipelineCardRecord::default();
        let card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .insert_card(&CardSQLTableNames::Pipeline, &card)
            .await
            .unwrap();

        // check if the card was inserted
        let card_args = CardQueryArgs {
            uid: Some(pipeline_card.uid.clone()),
            ..Default::default()
        };
        let results = client
            .query_cards(&CardSQLTableNames::Pipeline, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // update the card
        pipeline_card.name = "UpdatedPipelineName".to_string();
        let updated_card = ServerCard::Pipeline(pipeline_card.clone());

        client
            .update_card(&CardSQLTableNames::Pipeline, &updated_card)
            .await
            .unwrap();

        // check if the card was updated
        let updated_results = client
            .query_cards(&CardSQLTableNames::Pipeline, &card_args)
            .await
            .unwrap();

        assert_eq!(updated_results.len(), 1);
        if let CardResults::Pipeline(cards) = updated_results {
            assert_eq!(cards[0].name, "UpdatedPipelineName");
        }

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_unique_repos() {
        let client = get_client().await;

        // get unique repository names
        let repos = client
            .get_unique_repository_names(&CardSQLTableNames::Model)
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
            .query_stats(&CardSQLTableNames::Model, None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 10);
        assert_eq!(stats.nbr_versions, 10);
        assert_eq!(stats.nbr_repositories, 10);

        // query stats with search term
        let stats = client
            .query_stats(&CardSQLTableNames::Model, Some("Model1"))
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
            .query_page("name", 0, None, None, &CardSQLTableNames::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .query_page("name", 0, None, None, &CardSQLTableNames::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 10);

        // query page
        let results = client
            .query_page("name", 0, None, Some("repo3"), &CardSQLTableNames::Model)
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
            repository: Some("repo1".to_string()),
            ..Default::default()
        };

        let cards = client
            .query_cards(&CardSQLTableNames::Data, &args)
            .await
            .unwrap();

        let uid = match cards {
            CardResults::Data(cards) => cards[0].uid.clone(),
            _ => "".to_string(),
        };

        assert!(!uid.is_empty());

        // delete the card
        client
            .delete_card(&CardSQLTableNames::Data, &uid)
            .await
            .unwrap();

        // check if the card was deleted
        let args = CardQueryArgs {
            uid: Some(uid),
            ..Default::default()
        };

        let results = client
            .query_cards(&CardSQLTableNames::Data, &args)
            .await
            .unwrap();

        assert_eq!(results.len(), 0);
    }

    #[tokio::test]
    async fn test_enum_project_id() {
        let client = get_client().await;

        // get project id

        let project_id = client.get_project_id("test", "repo").await.unwrap();
        assert_eq!(project_id, 1);

        // get next project id
        let project_id = client.get_project_id("test1", "repo").await.unwrap();

        assert_eq!(project_id, 2);

        let args = CardQueryArgs {
            uid: None,
            name: Some("test".to_string()),
            repository: Some("repo".to_string()),
            ..Default::default()
        };
        let cards = client
            .query_cards(&CardSQLTableNames::Project, &args)
            .await
            .unwrap();

        assert_eq!(cards.len(), 1);
        cleanup();
    }

    // test run metric
    #[tokio::test]
    async fn test_enum_run_metric() {
        let client = get_client().await;

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let metric_names = vec!["metric1", "metric2", "metric3"];

        for name in metric_names {
            let metric = MetricRecord {
                run_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                step: None,
                timestamp: None,
                created_at: None,
                idx: None,
            };

            client.insert_run_metric(&metric).await.unwrap();
        }

        let records = client.get_run_metric(&uid, &Vec::new()).await.unwrap();

        let names = client.get_run_metric_names(&uid).await.unwrap();

        assert_eq!(records.len(), 3);

        // assert names = "metric1"
        assert_eq!(names.len(), 3);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_hardware_metric() {
        let client = get_client().await;

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut metrics = vec![];

        // create a loop of 10
        for _ in 0..10 {
            let metric = HardwareMetricsRecord {
                run_uid: uid.clone(),
                created_at: get_utc_datetime(),
                ..Default::default()
            };

            metrics.push(metric);
        }

        client.insert_hardware_metrics(&metrics).await.unwrap();
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
                run_uid: uid.clone(),
                name: format!("param{}", i),
                ..Default::default()
            };

            params.push(parameter);
        }

        client.insert_run_parameters(&params).await.unwrap();
        let records = client.get_run_parameter(&uid, &Vec::new()).await.unwrap();

        assert_eq!(records.len(), 10);

        let param_records = client
            .get_run_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(param_records.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_enum_user() {
        let client = get_client().await;

        let user = User::new("user".to_string(), "pass".to_string(), None, None);
        client.insert_user(&user).await.unwrap();

        let mut user = client.get_user("user").await.unwrap();
        assert_eq!(user.username, "user");

        // update user
        user.active = false;

        client.update_user(&user).await.unwrap();
        let user = client.get_user("user").await.unwrap();
        assert!(!user.active);

        cleanup();
    }
}
