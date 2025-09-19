use crate::{
    error::SqlError,
    sqlite::sql::{
        artifact::ArtifactLogicSqliteClient, audit::AuditLogicSqliteClient,
        card::CardLogicSqliteClient, experiment::ExperimentLogicSqliteClient,
        space::SpaceLogicSqliteClient, user::UserLogicSqliteClient,
    },
};
use opsml_settings::config::DatabaseSettings;
use sqlx::{sqlite::SqlitePoolOptions, Pool, Sqlite};
use std::path::Path;
use tracing::{debug, instrument};

#[derive(Debug, Clone)]
pub struct SqliteClient {
    pub pool: Pool<Sqlite>,

    // The SqliteClient is a parent struct that holds instances of various logic clients.
    // Each logic client is responsible for a specific domain (e.g., cards, experiments, etc).
    pub card: CardLogicSqliteClient,
    pub exp: ExperimentLogicSqliteClient,
    pub artifact: ArtifactLogicSqliteClient,
    pub user: UserLogicSqliteClient,
    pub space: SpaceLogicSqliteClient,
    pub audit: AuditLogicSqliteClient,
}

impl SqliteClient {
    pub async fn new(settings: &DatabaseSettings) -> Result<SqliteClient, SqlError> {
        // Create SQLite file if it doesn't exist and not in-memory
        if !settings.connection_uri.contains(":memory:") {
            let uri = settings.connection_uri.replace("sqlite://", "");
            let path = Path::new(&uri);

            if !path.exists() {
                debug!("SQLite file does not exist, creating file at: {}", uri);

                // Ensure parent directory exists
                if let Some(parent) = path.parent() {
                    if !parent.exists() {
                        std::fs::create_dir_all(parent)
                            .map_err(|e| SqlError::ConnectionError(sqlx::Error::Io(e)))?;
                    }
                }

                // Create the file
                std::fs::File::create(&uri)
                    .map_err(|e| SqlError::ConnectionError(sqlx::Error::Io(e)))?;
            }
        }

        let pool = SqlitePoolOptions::new()
            .max_connections(settings.max_connections)
            .connect(&settings.connection_uri)
            .await
            .map_err(SqlError::ConnectionError)?;

        // sqlx pools are wrapped in Arc, so cloning is cheap
        let client = SqliteClient {
            card: CardLogicSqliteClient::new(&pool),
            exp: ExperimentLogicSqliteClient::new(&pool),
            artifact: ArtifactLogicSqliteClient::new(&pool),
            user: UserLogicSqliteClient::new(&pool),
            space: SpaceLogicSqliteClient::new(&pool),
            audit: AuditLogicSqliteClient::new(&pool),
            pool,
        };

        // Run migrations
        client.run_migrations().await?;

        debug!("SQLite client initialized successfully");
        Ok(client)
    }

    #[instrument(skip(self))]
    pub async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running SQLite migrations");
        sqlx::migrate!("src/sqlite/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;
        debug!("SQLite migrations completed successfully");
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
    use crate::traits::{
        ArtifactLogicTrait, AuditLogicTrait, CardLogicTrait, ExperimentLogicTrait, SpaceLogicTrait,
        UserLogicTrait,
    };
    use opsml_settings::config::DatabaseSettings;
    use opsml_types::contracts::{ArtifactKey, ArtifactQueryArgs, AuditEvent, SpaceNameEvent};
    use opsml_types::SqlType;
    use opsml_types::{
        cards::CardTable,
        contracts::{ArtifactType, CardQueryArgs},
        RegistryType,
    };
    use opsml_utils::utils::get_utc_datetime;
    use semver::Version;
    use std::env;

    const SPACE: &str = "space";

    async fn test_card_crud(
        client: &SqliteClient,
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

    #[tokio::test]
    async fn test_sqlite() {
        let config = DatabaseSettings {
            connection_uri: "sqlite::memory:".to_string(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let _client = SqliteClient::new(&config).await;
    }

    // create test for non-memory sqlite

    #[tokio::test]
    async fn test_sqlite_versions() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

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

        let versions = client
            .card
            .get_versions(
                &CardTable::Data,
                "repo1",
                "Data1",
                Some("2.0.0".to_string()),
            )
            .await
            .unwrap();
        assert_eq!(versions.len(), 1);

        let versions = client
            .card
            .get_versions(&CardTable::Data, "repo1", "Data1", Some("2".to_string()))
            .await
            .unwrap();

        assert_eq!(versions.len(), 4);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_crud_cards() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_unique_repos() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // get unique space names
        let repos = client
            .card
            .get_unique_space_names(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 10);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_query_stats() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // query stats
        let stats = client
            .card
            .query_stats(&CardTable::Model, None, None)
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 10);
        assert_eq!(stats.nbr_versions, 10);
        assert_eq!(stats.nbr_spaces, 10);

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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_query_page() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

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

        assert_eq!(results.len(), 10);

        // query page
        let results = client
            .card
            .query_page("name", 1, None, Some("repo3"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_version_page() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();
        sqlx::query(&script).execute(&client.pool).await.unwrap();

        // query page
        let results = client
            .card
            .version_page(1, Some("repo1"), Some("Model1"), &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        cleanup();
    }

    // test run metric
    #[tokio::test]
    async fn test_sqlite_run_metric() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

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
        assert_eq!(names.len(), 5);

        let eval_records = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), Some(true))
            .await
            .unwrap();

        assert_eq!(eval_records.len(), 2);

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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_hardware_metric() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // create a loop of 10

        let metric = HardwareMetricsRecord {
            experiment_uid: uid.clone(),
            created_at: get_utc_datetime(),
            ..Default::default()
        };

        client.exp.insert_hardware_metrics(&metric).await.unwrap();
        let records = client.exp.get_hardware_metric(&uid).await.unwrap();

        assert_eq!(records.len(), 1);

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_parameter() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_sqlite_test.sql").unwrap();

        sqlx::query(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();
        let mut params = vec![];

        // create a loop of 10
        for i in 0..10 {
            let parameter = ParameterRecord {
                experiment_uid: uid.clone(),
                name: format!("param{i}"),
                ..Default::default()
            };

            params.push(parameter.clone());
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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_user() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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

        let mut user_to_update = client.user.get_user("user", None).await.unwrap().unwrap();

        assert_eq!(user_to_update.username, "user");
        assert_eq!(user_to_update.password_hash, "pass");
        assert_eq!(user_to_update.group_permissions, vec!["user"]);
        assert_eq!(user_to_update.email, "email");

        // update user
        user_to_update.active = false;
        user_to_update.refresh_token = Some("token".to_string());

        client.user.update_user(&user_to_update).await.unwrap();
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

        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_artifact_keys() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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
    async fn test_sqlite_insert_operation() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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
    async fn test_sqlite_get_load_card_key() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();
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
            space: data_card.space.clone(),
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

        assert_eq!(key.uid, data_card.uid);
        assert_eq!(key.encrypted_key, encrypted_key);

        let _ = client
            .artifact
            .get_artifact_key_from_path(&key.storage_key, &RegistryType::Data.to_string())
            .await
            .unwrap()
            .unwrap();

        // delete
        client
            .artifact
            .delete_artifact_key(&data_card.uid, &RegistryType::Data.to_string())
            .await
            .unwrap();
    }

    #[tokio::test]
    async fn test_sqlite_crud_space_record() {
        cleanup();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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

        // delete space name record
        client
            .space
            .delete_space_name_record(&data_card.space, &data_card.name, &RegistryType::Data)
            .await
            .unwrap();
        cleanup();
    }

    #[tokio::test]
    async fn test_sqlite_log_artifact() {
        cleanup();
        let name = "my_file.json".to_string();

        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        let client = SqliteClient::new(&config).await.unwrap();

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

        // assert artifact types
        assert_eq!(artifacts[0].artifact_type, ArtifactType::Generic);
        assert_eq!(artifacts[1].artifact_type, ArtifactType::Figure);
    }
}
