use crate::error::SqlError;
use crate::postgres::sql::{
    artifact::ArtifactLogicPostgresClient, audit::AuditLogicPostgresClient,
    card::CardLogicPostgresClient, evaluation::EvaluationLogicPostgresClient,
    experiment::ExperimentLogicPostgresClient, space::SpaceLogicPostgresClient,
    user::UserLogicPostgresClient,
};

use opsml_settings::config::DatabaseSettings;
use sqlx::ConnectOptions;
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions, Postgres},
    Pool,
};
use tracing::debug;

#[derive(Debug, Clone)]
pub struct PostgresClient {
    pub pool: Pool<Postgres>,
    pub card: CardLogicPostgresClient,
    pub exp: ExperimentLogicPostgresClient,
    pub artifact: ArtifactLogicPostgresClient,
    pub user: UserLogicPostgresClient,
    pub space: SpaceLogicPostgresClient,
    pub audit: AuditLogicPostgresClient,
    pub eval: EvaluationLogicPostgresClient,
}

impl PostgresClient {
    pub async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        let mut opts: PgConnectOptions = settings.connection_uri.parse()?;

        opts = opts.log_statements(tracing::log::LevelFilter::Off);

        let pool = PgPoolOptions::new()
            .max_connections(settings.max_connections)
            .connect_with(opts)
            .await
            .map_err(SqlError::ConnectionError)?;

        let client = PostgresClient {
            card: CardLogicPostgresClient::new(&pool),
            exp: ExperimentLogicPostgresClient::new(&pool),
            artifact: ArtifactLogicPostgresClient::new(&pool),
            user: UserLogicPostgresClient::new(&pool),
            space: SpaceLogicPostgresClient::new(&pool),
            audit: AuditLogicPostgresClient::new(&pool),
            eval: EvaluationLogicPostgresClient::new(&pool),
            pool,
        };

        // run migrations
        client.run_migrations().await?;

        Ok(client)
    }

    async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running migrations");
        sqlx::migrate!("src/postgres/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use super::*;
    use crate::schemas::schema::{
        ArtifactSqlRecord, AuditCardRecord, CardResults, DataCardRecord, ExperimentCardRecord,
        HardwareMetricsRecord, MetricRecord, ModelCardRecord, ParameterRecord, PromptCardRecord,
        ServerCard, ServiceCardRecord, User,
    };
    use crate::schemas::EvaluationSqlRecord;
    use crate::traits::EvaluationLogicTrait;
    use crate::traits::{
        ArtifactLogicTrait, AuditLogicTrait, CardLogicTrait, ExperimentLogicTrait, SpaceLogicTrait,
        UserLogicTrait,
    };
    use opsml_settings::config::DatabaseSettings;
    use opsml_types::contracts::{
        evaluation::{EvaluationProvider, EvaluationType},
        ArtifactKey, ArtifactQueryArgs, AuditEvent, SpaceNameEvent,
    };
    use opsml_types::CommonKwargs;
    use opsml_types::SqlType;
    use opsml_types::{
        cards::CardTable,
        contracts::{
            ArtifactType, CardQueryArgs, DeploymentConfig, McpCapability, McpConfig, McpTransport,
            Resources, ServiceConfig, ServiceQueryArgs, ServiceType, SpaceRecord,
        },
        RegistryType,
    };
    use opsml_utils::utils::get_utc_datetime;
    use semver::Version;
    use sqlx::types::Json;
    use std::env;

    const SPACE: &str = "my_space";
    pub async fn cleanup(pool: &Pool<Postgres>) {
        sqlx::raw_sql(
            r#"
            DELETE 
            FROM opsml_data_registry;

            DELETE 
            FROM opsml_model_registry;

            DELETE
            FROM opsml_experiment_registry;

            DELETE
            FROM opsml_audit_registry;

            DELETE
            FROM opsml_experiment_metric;

            DELETE
            FROM opsml_experiment_hardware_metric;

            DELETE
            FROM opsml_experiment_parameter;

            DELETE
            FROM opsml_prompt_registry;

            DELETE
            FROM opsml_user;

            DELETE
            FROM opsml_artifact_key;

            DELETE
            FROM opsml_audit_event;

            DELETE
            FROM opsml_service_registry;

            DELETE
            FROM opsml_artifact_registry;

            DELETE
            FROM opsml_space;

            DELETE
            FROM opsml_evaluation_registry;
            "#,
        )
        .fetch_all(pool)
        .await
        .unwrap();
    }

    async fn test_card_crud(
        client: &PostgresClient,
        table: &CardTable,
        updated_name: &str,
    ) -> Result<(), SqlError> {
        // Create initial card
        let card = match table {
            CardTable::Data => ServerCard::Data(DataCardRecord::default()),
            CardTable::Model => ServerCard::Model(ModelCardRecord::default()),
            CardTable::Experiment => ServerCard::Experiment(ExperimentCardRecord::default()),
            CardTable::Audit => ServerCard::Audit(AuditCardRecord::default()),
            CardTable::Prompt => ServerCard::Prompt(PromptCardRecord::default()),
            CardTable::Service => ServerCard::Service(ServiceCardRecord::default()),
            _ => panic!("Invalid card type"),
        };

        // Get UID for queries
        let uid = match &card {
            ServerCard::Data(c) => c.uid.clone(),
            ServerCard::Model(c) => c.uid.clone(),
            ServerCard::Experiment(c) => c.uid.clone(),
            ServerCard::Audit(c) => c.uid.clone(),
            ServerCard::Prompt(c) => c.uid.clone(),
            ServerCard::Service(c) => c.uid.clone(),
        };

        // Test Insert
        client.card.insert_card(table, &card).await?;

        // Verify Insert
        let card_args = CardQueryArgs {
            uid: Some(uid.clone()),
            ..Default::default()
        };
        let results = client.card.query_cards(table, &card_args).await?;
        assert_eq!(results.len(), 1);

        // Create updated card with new name
        let updated_card = match table {
            CardTable::Data => {
                let c = DataCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Data(c)
            }
            CardTable::Model => {
                let c = ModelCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };

                ServerCard::Model(c)
            }
            CardTable::Experiment => {
                let c = ExperimentCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Experiment(c)
            }
            CardTable::Audit => {
                let c = AuditCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Audit(c)
            }
            CardTable::Prompt => {
                let c = PromptCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Prompt(c)
            }
            CardTable::Service => {
                let c = ServiceCardRecord {
                    uid: uid.clone(),
                    name: updated_name.to_string(),
                    ..Default::default()
                };
                ServerCard::Service(c)
            }
            _ => panic!("Invalid card type"),
        };

        // Test Update
        client.card.update_card(table, &updated_card).await?;

        // Verify Update
        let updated_results = client.card.query_cards(table, &card_args).await?;
        assert_eq!(updated_results.len(), 1);

        // Verify updated name
        match updated_results {
            CardResults::Data(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Model(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Experiment(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Audit(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Prompt(cards) => assert_eq!(cards[0].name, updated_name),
            CardResults::Service(cards) => assert_eq!(cards[0].name, updated_name),
        }

        // delete card
        client.card.delete_card(table, &uid).await?;

        // Verify Delete
        let deleted_results = client.card.query_cards(table, &card_args).await?;
        assert_eq!(deleted_results.len(), 0);

        Ok(())
    }

    pub fn db_config() -> DatabaseSettings {
        DatabaseSettings {
            connection_uri: env::var("OPSML_TRACKING_URI").unwrap_or_else(|_| {
                "postgres://postgres:postgres@localhost:5432/postgres".to_string()
            }),
            max_connections: 1,
            sql_type: SqlType::Postgres,
        }
    }

    pub async fn db_client() -> PostgresClient {
        let config = db_config();
        let client = PostgresClient::new(&config).await.unwrap();

        cleanup(&client.pool).await;

        client
    }

    #[tokio::test]
    async fn test_postgres() {
        let _client = db_client().await;
        // Add assertions or further test logic here
    }

    #[tokio::test]
    async fn test_postgres_versions() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query all versions
        // get versions (should return 1)
        let versions = client
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", None)
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        // check star pattern
        let versions = client
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 10);

        let versions = client
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("1.*".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        let versions = client
            .card
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
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 4);

        // check tilde pattern
        let versions = client
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("~1.1".to_string()))
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);

        // check tilde pattern
        let versions = client
            .card
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
            .card
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("^2.0.0".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 2);
    }

    #[tokio::test]
    async fn test_postgres_query_cards() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // check if uid exists
        let exists = client
            .card
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
            .card
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
            .card
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
            .card
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
            .card
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
            .card
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
            .card
            .query_cards(&CardTable::Data, &card_args)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // check if uid exists
        let exists = client
            .card
            .check_uid_exists("550e8400-e29b-41d4-a716-446655440000", &CardTable::Data)
            .await
            .unwrap();

        assert!(exists);
    }

    #[tokio::test]
    async fn test_postgres_crud_cards() {
        let client = db_client().await;

        test_card_crud(&client, &CardTable::Data, "UpdatedDataName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Model, "UpdatedModelName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Experiment, "UpdatedRunName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Audit, "UpdatedAuditName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Prompt, "UpdatedPromptName")
            .await
            .unwrap();
        test_card_crud(&client, &CardTable::Service, "UpdatedDeckName")
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_unique_repos() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // get unique space names
        let repos = client
            .card
            .get_unique_space_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 9);
    }

    #[tokio::test]
    async fn test_postgres_query_stats() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query stats
        let stats = client
            .card
            .query_stats(&CardTable::Model, None, None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 9);
        assert_eq!(stats.nbr_versions, 9);
        assert_eq!(stats.nbr_spaces, 9);

        // query stats with search term
        let stats = client
            .card
            .query_stats(&CardTable::Model, Some("Model1"), None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2); // for Model1 and Model10

        let stats = client
            .card
            .query_stats(&CardTable::Model, Some("Model1"), Some("repo1"))
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 1); // for Model1

        // query page
        let results = client
            .card
            .query_page("name", 1, None, None, &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .card
            .query_page("name", 1, None, None, &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 9);

        // query page
        let results = client
            .card
            .query_page("name", 1, None, Some("repo4"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_version_page() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query page
        let results = client
            .card
            .version_page(1, Some("repo1"), Some("Model1"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_run_metrics() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let metric_names = vec!["metric1", "metric2", "metric3"];
        let eval_metric_names = vec!["eval_metric1", "eval_metric2"];

        for name in metric_names {
            let metric = MetricRecord {
                experiment_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                ..Default::default()
            };

            client.exp.insert_experiment_metric(&metric).await.unwrap();
        }

        for name in eval_metric_names {
            let metric = MetricRecord {
                experiment_uid: uid.clone(),
                name: name.to_string(),
                value: 1.0,
                is_eval: true,
                ..Default::default()
            };

            client.exp.insert_experiment_metric(&metric).await.unwrap();
        }

        let records = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), None)
            .await
            .unwrap();

        let names = client.exp.get_experiment_metric_names(&uid).await.unwrap();

        assert_eq!(records.len(), 5);

        // assert names = "metric1"
        assert_eq!(names.len(), 5);

        let eval_metric_records = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), Some(true))
            .await
            .unwrap();

        assert_eq!(eval_metric_records.len(), 2);
        // insert vec
        let records = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "vec1".to_string(),
                value: 1.0,
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "vec2".to_string(),
                value: 1.0,
                ..Default::default()
            },
        ];

        client
            .exp
            .insert_experiment_metrics(&records)
            .await
            .unwrap();

        let records = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), None)
            .await
            .unwrap();

        assert_eq!(records.len(), 7);
    }

    #[tokio::test]
    async fn test_postgres_hardware_metric() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // create a loop of 10
        let metrics = HardwareMetricsRecord {
            experiment_uid: uid.clone(),
            created_at: get_utc_datetime(),
            ..Default::default()
        };

        client.exp.insert_hardware_metrics(&metrics).await.unwrap();
        let records = client.exp.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_parameter() {
        let client = db_client().await;
        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let param = ParameterRecord {
                experiment_uid: uid.clone(),
                name: format!("param{i}"),
                ..Default::default()
            };

            params.push(param);
        }

        client
            .exp
            .insert_experiment_parameters(&params)
            .await
            .unwrap();
        let records = client
            .exp
            .get_experiment_parameter(&uid, &Vec::new())
            .await
            .unwrap();

        assert_eq!(records.len(), 10);

        let param_records = client
            .exp
            .get_experiment_parameter(&uid, &["param1".to_string()])
            .await
            .unwrap();

        assert_eq!(param_records.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_user() {
        let client = db_client().await;
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

        client.user.insert_user(&user).await.unwrap();
        client.user.insert_user(&sso_user).await.unwrap();

        // Read
        let mut user = client.user.get_user("user", None).await.unwrap().unwrap();

        assert_eq!(user.username, "user");
        assert_eq!(user.group_permissions, vec!["user"]);
        assert_eq!(user.email, "email");

        // update user
        user.active = false;
        user.refresh_token = Some("token".to_string());

        // Update
        client.user.update_user(&user).await.unwrap();
        let user = client.user.get_user("user", None).await.unwrap().unwrap();
        assert!(!user.active);
        assert_eq!(user.refresh_token.unwrap(), "token");

        // get users
        let users = client.user.get_users().await.unwrap();
        assert_eq!(users.len(), 2);

        let user = client
            .user
            .get_user("sso_user", Some("sso"))
            .await
            .unwrap()
            .unwrap();
        assert!(user.active);

        // delete
        client.user.delete_user("sso_user").await.unwrap();

        // get last admin
        let is_last_admin = client.user.is_last_admin("user").await.unwrap();
        assert!(!is_last_admin);

        // delete
        client.user.delete_user("user").await.unwrap();
    }

    #[tokio::test]
    async fn test_postgres_artifact_keys() {
        let client = db_client().await;

        let encrypted_key: Vec<u8> = (0..32).collect();

        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.artifact.insert_artifact_key(&key).await.unwrap();

        let key = client
            .artifact
            .get_artifact_key(&key.uid, &key.registry_type.to_string())
            .await
            .unwrap();

        assert_eq!(key.uid, "550e8400-e29b-41d4-a716-446655440000");

        // update key
        let encrypted_key: Vec<u8> = (32..64).collect();
        let key = ArtifactKey {
            uid: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.artifact.update_artifact_key(&key).await.unwrap();

        let key = client
            .artifact
            .get_artifact_key(&key.uid, &key.registry_type.to_string())
            .await
            .unwrap();

        assert_eq!(key.encrypted_key, encrypted_key);
    }

    #[tokio::test]
    async fn test_postgres_insert_operation() {
        let client = db_client().await;

        client
            .audit
            .insert_audit_event(AuditEvent::default())
            .await
            .unwrap();

        // check if the operation was inserted
        let query = r#"SELECT username  FROM opsml_audit_event WHERE username = 'guest';"#;
        let result: String = sqlx::query_scalar(query)
            .fetch_one(&client.pool)
            .await
            .unwrap();

        assert_eq!(result, "guest");
    }

    #[tokio::test]
    async fn test_postgres_get_load_card_key() {
        let client = db_client().await;
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());

        client
            .card
            .insert_card(&CardTable::Data, &card)
            .await
            .unwrap();
        let encrypted_key: Vec<u8> = (0..32).collect();
        let key = ArtifactKey {
            uid: data_card.uid.clone(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Data,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.artifact.insert_artifact_key(&key).await.unwrap();

        // test uid (testing to ensure it doesnt fail)
        let _key = client
            .card
            .get_card_key_for_loading(
                &CardTable::Data,
                &CardQueryArgs {
                    uid: Some(data_card.uid.clone()),
                    limit: Some(1),
                    ..Default::default()
                },
            )
            .await
            .unwrap();

        // test args
        let key = client
            .card
            .get_card_key_for_loading(
                &CardTable::Data,
                &CardQueryArgs {
                    space: Some(data_card.space.clone()),
                    name: Some(data_card.name.clone()),
                    version: Some(data_card.version.to_string()),
                    ..Default::default()
                },
            )
            .await
            .unwrap();

        let _ = client
            .artifact
            .get_artifact_key_from_path(&key.storage_key, &RegistryType::Data.to_string())
            .await
            .unwrap()
            .unwrap();

        assert_eq!(key.uid, data_card.uid);
        assert_eq!(key.encrypted_key, encrypted_key);

        // delete
        client
            .artifact
            .delete_artifact_key(&data_card.uid, &RegistryType::Data.to_string())
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_crud_space_record() {
        let client = db_client().await;

        // create a new space record
        let space_record = SpaceRecord {
            space: CommonKwargs::Undefined.to_string(),
            description: "Space description".to_string(),
        };

        client
            .space
            .insert_space_record(&space_record)
            .await
            .unwrap();

        // insert datacard
        let data_card = DataCardRecord::default();
        let card = ServerCard::Data(data_card.clone());
        client
            .card
            .insert_card(&CardTable::Data, &card)
            .await
            .unwrap();

        // insert modelcard
        let model_card = ModelCardRecord::default();
        let card = ServerCard::Model(model_card.clone());
        client
            .card
            .insert_card(&CardTable::Model, &card)
            .await
            .unwrap();

        let space_event = SpaceNameEvent {
            space: data_card.space.clone(),
            name: data_card.name.clone(),
            registry_type: RegistryType::Data,
        };
        client
            .space
            .insert_space_name_record(&space_event)
            .await
            .unwrap();

        let space_event = SpaceNameEvent {
            space: model_card.space.clone(),
            name: model_card.name.clone(),
            registry_type: RegistryType::Model,
        };

        client
            .space
            .insert_space_name_record(&space_event)
            .await
            .unwrap();

        // get space stats
        let stats = client.space.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);

        // assert model_count
        assert_eq!(stats[0].data_count, 1);

        //create a new modelcard
        let model_card2 = ModelCardRecord {
            name: "Model2".to_string(),
            ..Default::default()
        };
        let card = ServerCard::Model(model_card2.clone());
        client
            .card
            .insert_card(&CardTable::Model, &card)
            .await
            .unwrap();

        // update space stats again
        let space_event = SpaceNameEvent {
            space: model_card2.space.clone(),
            name: model_card2.name.clone(),
            registry_type: RegistryType::Model,
        };

        client
            .space
            .insert_space_name_record(&space_event)
            .await
            .unwrap();
        // get space stats again

        let stats = client.space.get_all_space_stats().await.unwrap();
        assert_eq!(stats.len(), 1);

        // assert model_count
        assert_eq!(stats[0].model_count, 2);

        // update space record
        let updated_space_record = SpaceRecord {
            space: model_card2.space.clone(),
            description: "Updated Space description".to_string(),
        };
        client
            .space
            .update_space_record(&updated_space_record)
            .await
            .unwrap();

        // get space record
        let record = client
            .space
            .get_space_record(&model_card2.space)
            .await
            .unwrap()
            .unwrap();

        assert_eq!(record.description, "Updated Space description");

        // delete
        client
            .space
            .delete_space_record(&model_card2.space)
            .await
            .unwrap();

        // get space stats again
        let record = client
            .space
            .get_space_record(&model_card2.space)
            .await
            .unwrap();
        assert_eq!(record, None);

        // delete space name record
        client
            .space
            .delete_space_name_record(&model_card2.space, &model_card2.name, &RegistryType::Model)
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_postgres_log_artifact() {
        let client = db_client().await;
        let name = "my_file.json".to_string();

        // create a new artifact record
        let artifact_record1 = ArtifactSqlRecord::new(
            SPACE.to_string(),
            name.clone(),
            Version::new(0, 0, 0),
            "png".to_string(),
            ArtifactType::Generic.to_string(),
        );
        client
            .artifact
            .insert_artifact_record(&artifact_record1)
            .await
            .unwrap();

        let artifact_record2 = ArtifactSqlRecord::new(
            SPACE.to_string(),
            name.clone(),
            Version::new(0, 0, 0),
            "png".to_string(),
            ArtifactType::Figure.to_string(),
        );

        client
            .artifact
            .insert_artifact_record(&artifact_record2)
            .await
            .unwrap();

        // query artifacts
        let artifacts = client
            .artifact
            .query_artifacts(&ArtifactQueryArgs {
                space: Some(SPACE.to_string()),
                name: Some(name.clone()),
                ..Default::default()
            })
            .await
            .unwrap();
        assert_eq!(artifacts.len(), 2);

        assert_eq!(artifacts[0].artifact_type, ArtifactType::Generic);
        assert_eq!(artifacts[1].artifact_type, ArtifactType::Figure);
    }

    #[tokio::test]
    async fn test_postgres_insert_eval() {
        let client = db_client().await;
        let eval_record = EvaluationSqlRecord::new(
            "test".to_string(),
            EvaluationType::LLM,
            EvaluationProvider::Opsml,
        );
        let uid = eval_record.uid.clone();
        client
            .eval
            .insert_evaluation_record(eval_record)
            .await
            .unwrap();

        let record = client.eval.get_evaluation_record(&uid).await.unwrap();

        assert_eq!(record.name, "test");
    }

    #[tokio::test]
    async fn test_postgres_recent_services() {
        let client = db_client().await;

        // create 1st service card
        let card1 = ServiceCardRecord {
            name: "Service0".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Mcp.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            ..Default::default()
        };
        client
            .card
            .insert_card(&CardTable::Service, &ServerCard::Service(card1))
            .await
            .unwrap();

        // create 2nd card
        let card2 = ServiceCardRecord {
            name: "Service1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Api.to_string(),
            ..Default::default()
        };
        client
            .card
            .insert_card(&CardTable::Service, &ServerCard::Service(card2))
            .await
            .unwrap();

        // Create 3rd card, but new version
        let mcp_config = McpConfig {
            capabilities: vec![McpCapability::Tools],
            transport: McpTransport::Http,
        };
        let deploy = DeploymentConfig {
            environment: "dev".to_string(),
            provider: Some("development".to_string()),
            location: Some(vec!["local".to_string()]),
            endpoints: vec!["http://localhost:8000".to_string()],
            resources: Some(Resources {
                cpu: 2,
                memory: "4GB".to_string(),
                storage: "10GB".to_string(),
                gpu: None,
            }),
            links: None,
        };
        let card3 = ServiceCardRecord {
            name: "Service0".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Mcp.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            service_config: Json(ServiceConfig {
                mcp: Some(mcp_config),
                ..Default::default()
            }),
            deployment: Some(Json(vec![deploy])),
            ..Default::default()
        };

        // wait 1 second to ensure different created_at timestamp
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        client
            .card
            .insert_card(&CardTable::Service, &ServerCard::Service(card3))
            .await
            .unwrap();

        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: None,
                service_type: None,
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 2);

        // search by tag
        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: Some(vec!["tag1".to_string()]),
                service_type: None,
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 1);

        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: None,
                service_type: Some(ServiceType::Mcp.to_string()),
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 1);

        // check that endpoint is populated
        assert!(services[0].deployment.is_some());
        let deployment = services[0].deployment.as_ref().unwrap();
        assert_eq!(deployment.len(), 1);
        assert_eq!(deployment[0].environment, "dev");
        assert_eq!(deployment[0].endpoints.len(), 1);
        assert_eq!(deployment[0].endpoints[0], "http://localhost:8000");
    }
}
