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
    Pool,
    postgres::{PgConnectOptions, PgPoolOptions, Postgres},
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
    use crate::schemas::EvaluationSqlRecord;
    use crate::schemas::schema::{
        ArtifactSqlRecord, AuditCardRecord, CardResults, DataCardRecord, ExperimentCardRecord,
        HardwareMetricsRecord, MetricRecord, ModelCardRecord, ParameterRecord, PromptCardRecord,
        ServerCard, ServiceCardRecord, User,
    };
    use crate::traits::EvaluationLogicTrait;
    use crate::traits::{
        ArtifactLogicTrait, AuditLogicTrait, CardLogicTrait, ExperimentLogicTrait, SpaceLogicTrait,
        UserLogicTrait,
    };
    use opsml_settings::config::DatabaseSettings;
    use opsml_types::CommonKwargs;
    use opsml_types::SqlType;
    use opsml_types::contracts::VersionCursor;
    use opsml_types::contracts::agent::{
        AgentCapabilities, AgentInterface, AgentProvider, AgentSkill, AgentSpec,
        SecurityRequirement,
    };
    use opsml_types::contracts::{
        ArtifactKey, ArtifactQueryArgs, AuditEvent, SpaceNameEvent,
        evaluation::{EvaluationProvider, EvaluationType},
    };
    use opsml_types::{
        RegistryType,
        cards::CardTable,
        contracts::{
            ArtifactType, CardQueryArgs, DeploymentConfig, McpCapability, McpConfig, McpTransport,
            Resources, ServiceConfig, ServiceQueryArgs, ServiceType, SpaceRecord,
        },
    };
    use opsml_utils::utils::get_utc_datetime;
    use semver::Version;
    use sqlx::types::Json;
    use std::{env, vec};
    use tracing::error;

    const SPACE: &str = "my_space";

    fn example_agent_spec() -> AgentSpec {
        AgentSpec::new_rs(
            "TestAgent".to_string(),
            "A test agent for SQL integration tests".to_string(),
            "1.0.0".to_string(),
            vec![AgentInterface::new(
                "http://localhost:8000".to_string(),
                "HTTP".to_string(),
                "1.0".to_string(),
                Some("tenant1".to_string()),
            )],
            AgentCapabilities::new(
                true,  // streaming
                false, // push_notifications
                false, // extended_agent_card
                None,  // extensions
            ),
            vec!["text".to_string()],
            vec!["json".to_string()],
            vec![opsml_types::contracts::SkillFormat::A2A(AgentSkill::new(
                "skill1".to_string(),
                "Echo".to_string(),
                "Echoes input text".to_string(),
                Some(vec!["test".to_string()]),
                Some(vec!["example input".to_string()]),
                Some(vec!["text".to_string()]),
                Some(vec!["text".to_string()]),
                Some(vec![SecurityRequirement::new(vec!["apiKey".to_string()])]),
            ))],
            Some(AgentProvider::new(
                Some("TestOrg".to_string()),
                Some("https://test.org".to_string()),
            )),
            Some("https://docs.test.org".to_string()),
            Some("https://test.org/icon.png".to_string()),
            None, // security_schemes
            Some(vec![SecurityRequirement::new(vec!["apiKey".to_string()])]),
            None, // signatures
        )
        .unwrap()
    }

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
            FROM opsml_mcp_registry;

            DELETE
            FROM opsml_agent_registry;

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
            CardTable::Service => ServerCard::Service(Box::default()),
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
        client
            .card
            .insert_card(table, &card)
            .await
            .inspect_err(|e| error!("Failed to insert card: {e}"))?;

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
                ServerCard::Service(Box::new(c))
            }
            _ => panic!("Invalid card type"),
        };

        // Test Update
        client
            .card
            .update_card(table, &updated_card)
            .await
            .inspect_err(|e| {
                error!("Failed to update card: {:?}", e.to_string());
            })?;

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

        //cleanup(&client.pool).await;

        client
    }

    #[tokio::test]
    async fn test_postgres_client() {
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

        // unique tags
        let repos = client
            .card
            .get_unique_tags(&CardTable::Model)
            .await
            .unwrap();

        assert_eq!(repos.len(), 3);
    }

    #[tokio::test]
    async fn test_postgres_query_pagination() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // Test 1: Basic pagination with limit + 1 pattern
        let page1 = client
            .card
            .query_page("updated_at", 5, 0, None, &[], &[], &CardTable::Model)
            .await
            .unwrap();

        assert!(
            page1.len() <= 6,
            "Should return at most limit + 1 for has_next detection"
        );

        // Test 2: Second page - verify no overlap
        let page2 = client
            .card
            .query_page("updated_at", 5, 5, None, &[], &[], &CardTable::Model)
            .await
            .unwrap();

        let page1_uids: Vec<_> = page1.iter().take(5).map(|c| &c.uid).collect();
        let page2_uids: Vec<_> = page2.iter().take(5).map(|c| &c.uid).collect();

        for uid in &page2_uids {
            assert!(!page1_uids.contains(uid), "Pages should not overlap");
        }

        // Test 3: Search filter
        let search_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                Some("Model1"),
                &[],
                &[],
                &CardTable::Model,
            )
            .await
            .unwrap();

        for summary in search_results.iter().take(10) {
            assert!(
                summary.name.contains("Model1"),
                "All results should match search term"
            );
        }

        // Test 4: Space filter
        let space_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                None,
                &["repo1".to_string(), "repo2".to_string()],
                &[],
                &CardTable::Model,
            )
            .await
            .unwrap();

        for summary in space_results.iter().take(10) {
            assert!(
                summary.space == "repo1" || summary.space == "repo2",
                "Results should match space filter"
            );
        }

        // Test 5: Tag filter
        let tag_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                None,
                &[],
                &["hello".to_string()],
                &CardTable::Model,
            )
            .await
            .unwrap();

        assert!(
            tag_results.len() >= 2,
            "Should find models with 'hello' tag"
        );

        // Test 6: Combined filters (practical use case)
        let combined_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                Some("Model"),
                &["repo1".to_string()],
                &["hello".to_string()],
                &CardTable::Model,
            )
            .await
            .unwrap();

        for summary in combined_results.iter().take(10) {
            assert!(summary.name.contains("Model"), "Should match search");
            assert_eq!(summary.space, "repo1", "Should match space");
        }

        // Test 7: Sort by name
        let sorted_results = client
            .card
            .query_page("name", 5, 0, None, &[], &[], &CardTable::Model)
            .await
            .unwrap();

        if sorted_results.len() >= 2 {
            for i in 0..sorted_results.len().min(5) - 1 {
                assert!(
                    sorted_results[i].name >= sorted_results[i + 1].name,
                    "Results should be sorted by name DESC"
                );
            }
        }

        // Test 8: Version count accuracy
        let data_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                Some("Data1"),
                &[],
                &[],
                &CardTable::Data,
            )
            .await
            .unwrap();

        if let Some(data1) = data_results.iter().find(|s| s.name == "Data1") {
            assert_eq!(data1.versions, 10, "Data1 should have 10 versions");
        }

        // Test 9: Empty results (edge case)
        let empty_results = client
            .card
            .query_page(
                "updated_at",
                10,
                0,
                Some("NonExistentModel"),
                &[],
                &[],
                &CardTable::Model,
            )
            .await
            .unwrap();

        assert_eq!(empty_results.len(), 0, "Should return empty for no matches");

        // Test 10: Offset beyond results (edge case)
        let beyond_results = client
            .card
            .query_page("updated_at", 10, 100, None, &[], &[], &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(
            beyond_results.len(),
            0,
            "Should return empty when offset exceeds data"
        );
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
            .query_stats(&CardTable::Model, None, &[], &[])
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 9);
        assert_eq!(stats.nbr_versions, 9);
        assert_eq!(stats.nbr_spaces, 9);

        // query stats with search term
        let stats = client
            .card
            .query_stats(&CardTable::Model, Some("Model1"), &[], &[])
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2); // for Model1 and Model10

        let stats = client
            .card
            .query_stats(
                &CardTable::Model,
                Some("Model1"),
                &["repo1".to_string()],
                &[],
            )
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 1); // for Model1

        let stats = client
            .card
            .query_stats(&CardTable::Model, None, &[], &["hello".to_string()])
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 2);

        let stats = client
            .card
            .query_stats(&CardTable::Model, None, &[], &["v3".to_string()])
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 1);

        let stats = client
            .card
            .query_stats(
                &CardTable::Model,
                None,
                &[],
                &["v3".to_string(), "hello".to_string()],
            )
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 3);

        let stats = client
            .card
            .query_stats(
                &CardTable::Model,
                None,
                &[
                    "repo1".to_string(),
                    "repo2".to_string(),
                    "repo4".to_string(),
                ],
                &[],
            )
            .await
            .unwrap();

        assert_eq!(stats.nbr_names, 3);

        // query page
        let results = client
            .card
            .query_page("name", 1, 0, None, &[], &[], &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        // query page
        let results = client
            .card
            .query_page("name", 1, 0, None, &[], &[], &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        // query page
        let results = client
            .card
            .query_page(
                "name",
                1,
                0,
                None,
                &["repo4".to_string()],
                &[],
                &CardTable::Model,
            )
            .await
            .unwrap();

        assert_eq!(results.len(), 1);

        let results = client
            .card
            .query_page(
                "name",
                1,
                0,
                None,
                &[],
                &["hello".to_string()],
                &CardTable::Model,
            )
            .await
            .unwrap();

        assert_eq!(results.len(), 2);

        let results = client
            .card
            .query_page(
                "name",
                1,
                0,
                None,
                &[
                    "repo1".to_string(),
                    "repo2".to_string(),
                    "repo4".to_string(),
                ],
                &[],
                &CardTable::Model,
            )
            .await
            .unwrap();

        assert_eq!(results.len(), 2);
    }

    #[tokio::test]
    async fn test_postgres_version_page() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // Test 1: Initial page with cursor (offset 0)
        let cursor = VersionCursor::new(0, 30, "repo1".to_string(), "Model1".to_string());
        let results = client
            .card
            .version_page(&cursor, &CardTable::Model)
            .await
            .unwrap();

        // Should return limit + 1 for has_next detection (or fewer if less data exists)
        assert!(results.len() <= 31, "Should return at most limit + 1");

        // Based on your test data, Model1 should have 1 version
        assert_eq!(results.len(), 1, "Model1 should have 1 version");

        // Test 2: Verify version data
        if !results.is_empty() {
            assert_eq!(results[0].space, "repo1");
            assert_eq!(results[0].name, "Model1");
        }

        // Test 3: Test pagination with Data1 (which has 10 versions based on other tests)
        let cursor = VersionCursor::new(0, 5, "repo1".to_string(), "Data1".to_string());
        let page1_results = client
            .card
            .version_page(&cursor, &CardTable::Data)
            .await
            .unwrap();

        // Should return 6 results (5 + 1 for has_next detection)
        assert!(
            page1_results.len() <= 6,
            "Should return at most limit + 1 for first page"
        );

        // Test 4: Second page with offset
        let cursor = VersionCursor::new(5, 5, "repo1".to_string(), "Data1".to_string());
        let page2_results = client
            .card
            .version_page(&cursor, &CardTable::Data)
            .await
            .unwrap();

        assert!(
            page2_results.len() <= 6,
            "Should return at most limit + 1 for second page"
        );

        // Test 5: Verify no overlap between pages
        if page1_results.len() > 1 && page2_results.len() > 1 {
            let page1_versions: Vec<_> = page1_results.iter().take(5).map(|v| &v.version).collect();
            let page2_versions: Vec<_> = page2_results.iter().take(5).map(|v| &v.version).collect();

            for version in &page2_versions {
                assert!(
                    !page1_versions.contains(version),
                    "Pages should not have overlapping versions"
                );
            }
        }

        // Test 6: Verify ordering (should be DESC by created_at, then version components)
        if page1_results.len() >= 2 {
            for i in 0..page1_results.len() - 1 {
                let current = &page1_results[i];
                let next = &page1_results[i + 1];

                // Either created_at DESC or if same, version DESC
                assert!(
                    current.created_at >= next.created_at,
                    "Results should be ordered by created_at DESC"
                );
            }
        }

        // Test 7: Test with non-existent card
        let cursor = VersionCursor::new(0, 30, "repo1".to_string(), "NonExistent".to_string());
        let empty_results = client
            .card
            .version_page(&cursor, &CardTable::Model)
            .await
            .unwrap();

        assert_eq!(
            empty_results.len(),
            0,
            "Should return empty for non-existent card"
        );

        // Test 8: Test with offset beyond available data
        let cursor = VersionCursor::new(100, 30, "repo1".to_string(), "Data1".to_string());
        let beyond_results = client
            .card
            .version_page(&cursor, &CardTable::Data)
            .await
            .unwrap();

        assert_eq!(
            beyond_results.len(),
            0,
            "Should return empty when offset exceeds available versions"
        );
    }

    #[tokio::test]
    async fn test_postgres_dashboard_stats() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_dashboard.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        // query dashboard stats
        let stats = client.card.query_dashboard_stats().await.unwrap();

        assert_eq!(stats.nbr_data, 10);
        assert_eq!(stats.nbr_models, 9);
        assert_eq!(stats.nbr_experiments, 10);
        assert_eq!(stats.nbr_prompts, 0);
    }

    #[tokio::test]
    async fn test_postgres_experiment_metrics() {
        let client = db_client().await;

        // Run the SQL script to populate the database
        let script = std::fs::read_to_string("tests/populate_postgres_test.sql").unwrap();
        sqlx::raw_sql(&script).execute(&client.pool).await.unwrap();

        let uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

        // Test 1: Insert metrics with various steps to test sorting
        let metrics_with_steps = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "accuracy".to_string(),
                value: 0.85,
                step: Some(3),
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "accuracy".to_string(),
                value: 0.90,
                step: Some(1),
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "accuracy".to_string(),
                value: 0.95,
                step: Some(2),
                ..Default::default()
            },
            // Test null step handling (should sort to end with COALESCE)
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "accuracy".to_string(),
                value: 0.80,
                step: None,
                ..Default::default()
            },
        ];

        client
            .exp
            .insert_experiment_metrics(&metrics_with_steps)
            .await
            .unwrap();

        // Test 2: Insert metrics with different names to test name sorting
        let multi_name_metrics = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "loss".to_string(),
                value: 0.5,
                step: Some(1),
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "loss".to_string(),
                value: 0.3,
                step: Some(2),
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "f1_score".to_string(),
                value: 0.88,
                step: Some(1),
                ..Default::default()
            },
        ];

        client
            .exp
            .insert_experiment_metrics(&multi_name_metrics)
            .await
            .unwrap();

        // Test 3: Insert eval metrics
        let eval_metrics = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "eval_accuracy".to_string(),
                value: 0.92,
                step: Some(1),
                is_eval: true,
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "eval_loss".to_string(),
                value: 0.25,
                step: Some(1),
                is_eval: true,
                ..Default::default()
            },
        ];

        client
            .exp
            .insert_experiment_metrics(&eval_metrics)
            .await
            .unwrap();

        // Test 4: Query all metrics (empty names array) - tests CARDINALITY = 0 branch
        let all_metrics = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), None)
            .await
            .unwrap();

        assert_eq!(all_metrics.len(), 9, "Should retrieve all inserted metrics");

        // Test 5: Verify sorting by name ASC, step ASC
        // Metrics should be ordered: accuracy (steps 1,2,3,null), eval_accuracy, eval_loss, f1_score, loss (steps 1,2)
        assert_eq!(all_metrics[0].name, "accuracy");
        assert_eq!(
            all_metrics[0].step,
            Some(1),
            "First accuracy should be step 1"
        );
        assert_eq!(
            all_metrics[1].step,
            Some(2),
            "Second accuracy should be step 2"
        );
        assert_eq!(
            all_metrics[2].step,
            Some(3),
            "Third accuracy should be step 3"
        );
        assert_eq!(
            all_metrics[3].step, None,
            "Fourth accuracy should be None (sorted last via COALESCE)"
        );

        // Test 6: Filter by single name - tests name = ANY($2) with single element
        let accuracy_metrics = client
            .exp
            .get_experiment_metric(&uid, &["accuracy".to_string()], None)
            .await
            .unwrap();

        assert_eq!(
            accuracy_metrics.len(),
            4,
            "Should retrieve 4 accuracy metrics"
        );
        assert!(
            accuracy_metrics.iter().all(|m| m.name == "accuracy"),
            "All metrics should be named 'accuracy'"
        );
        // Verify sorting within single name
        assert_eq!(accuracy_metrics[0].step, Some(1));
        assert_eq!(accuracy_metrics[1].step, Some(2));
        assert_eq!(accuracy_metrics[2].step, Some(3));
        assert_eq!(accuracy_metrics[3].step, None);

        // Test 7: Filter by multiple names - tests name = ANY($2) with array
        let multi_name_filter = client
            .exp
            .get_experiment_metric(&uid, &["accuracy".to_string(), "loss".to_string()], None)
            .await
            .unwrap();

        assert_eq!(
            multi_name_filter.len(),
            6,
            "Should retrieve 4 accuracy + 2 loss metrics"
        );
        // Verify name ordering (accuracy before loss alphabetically)
        assert_eq!(multi_name_filter[0].name, "accuracy");
        assert_eq!(multi_name_filter[4].name, "loss");
        assert_eq!(multi_name_filter[5].name, "loss");

        // Test 8: Filter by is_eval = true - tests $3::boolean IS NULL OR is_eval = $3
        let eval_only = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), Some(true))
            .await
            .unwrap();

        assert_eq!(eval_only.len(), 2, "Should retrieve only eval metrics");
        assert!(
            eval_only.iter().all(|m| m.is_eval),
            "All metrics should be eval metrics"
        );
        assert_eq!(eval_only[0].name, "eval_accuracy");
        assert_eq!(eval_only[1].name, "eval_loss");

        // Test 9: Filter by is_eval = false
        let non_eval = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), Some(false))
            .await
            .unwrap();

        assert_eq!(non_eval.len(), 7, "Should retrieve only non-eval metrics");
        assert!(
            non_eval.iter().all(|m| !m.is_eval),
            "All metrics should be non-eval"
        );

        // Test 10: Combined filters - names array + is_eval
        let filtered_combo = client
            .exp
            .get_experiment_metric(&uid, &["accuracy".to_string()], Some(false))
            .await
            .unwrap();

        assert_eq!(
            filtered_combo.len(),
            4,
            "Should retrieve only non-eval accuracy metrics"
        );
        assert!(
            filtered_combo
                .iter()
                .all(|m| m.name == "accuracy" && !m.is_eval)
        );

        // Test 11: Verify created_at timestamp ordering for same name/step
        // Insert two metrics with identical name and step but different timestamps
        tokio::time::sleep(std::time::Duration::from_millis(10)).await;

        let timestamp_test_metrics = vec![
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "timestamp_test".to_string(),
                value: 1.0,
                step: Some(1),
                ..Default::default()
            },
            MetricRecord {
                experiment_uid: uid.clone(),
                name: "timestamp_test".to_string(),
                value: 2.0,
                step: Some(1),
                ..Default::default()
            },
        ];

        for metric in timestamp_test_metrics {
            client.exp.insert_experiment_metric(&metric).await.unwrap();
            tokio::time::sleep(std::time::Duration::from_millis(10)).await;
        }

        let timestamp_ordered = client
            .exp
            .get_experiment_metric(&uid, &["timestamp_test".to_string()], None)
            .await
            .unwrap();

        assert_eq!(timestamp_ordered.len(), 2);
        // Both have same name and step, so created_at ASC should determine order
        assert!(
            timestamp_ordered[0].created_at <= timestamp_ordered[1].created_at,
            "Should be ordered by created_at ASC"
        );
        assert_eq!(timestamp_ordered[0].value, 1.0);
        assert_eq!(timestamp_ordered[1].value, 2.0);

        // Test 12: Get unique metric names
        let metric_names = client.exp.get_experiment_metric_names(&uid).await.unwrap();

        assert!(metric_names.contains(&"accuracy".to_string()));
        assert!(metric_names.contains(&"loss".to_string()));
        assert!(metric_names.contains(&"eval_accuracy".to_string()));
        assert!(metric_names.contains(&"timestamp_test".to_string()));

        // Test 13: Empty names array with is_eval filter - tests CARDINALITY = 0 with eval filter
        let all_eval = client
            .exp
            .get_experiment_metric(&uid, &Vec::new(), Some(true))
            .await
            .unwrap();

        assert_eq!(all_eval.len(), 2);
        assert!(all_eval.iter().all(|m| m.is_eval));

        // Test 14: Non-existent metric name - tests empty result
        let non_existent = client
            .exp
            .get_experiment_metric(&uid, &["does_not_exist".to_string()], None)
            .await
            .unwrap();

        assert_eq!(
            non_existent.len(),
            0,
            "Should return empty for non-existent metric"
        );

        // Test 15: Large batch insert with multiple steps per metric
        let large_batch: Vec<MetricRecord> = (0..20)
            .flat_map(|step| {
                vec![
                    MetricRecord {
                        experiment_uid: uid.clone(),
                        name: "batch_metric_a".to_string(),
                        value: step as f64 * 0.1,
                        step: Some(step),
                        ..Default::default()
                    },
                    MetricRecord {
                        experiment_uid: uid.clone(),
                        name: "batch_metric_b".to_string(),
                        value: step as f64 * 0.2,
                        step: Some(step),
                        ..Default::default()
                    },
                ]
            })
            .collect();

        client
            .exp
            .insert_experiment_metrics(&large_batch)
            .await
            .unwrap();

        let batch_results = client
            .exp
            .get_experiment_metric(
                &uid,
                &["batch_metric_a".to_string(), "batch_metric_b".to_string()],
                None,
            )
            .await
            .unwrap();

        assert_eq!(batch_results.len(), 40, "Should retrieve all batch metrics");

        // Verify interleaved sorting: batch_metric_a (steps 0-19), then batch_metric_b (steps 0-19)
        for (i, _) in batch_results.iter().enumerate().take(20) {
            assert_eq!(batch_results[i].name, "batch_metric_a");
            assert_eq!(batch_results[i].step, Some(i as i32));
        }
        for (i, _) in batch_results.iter().enumerate().take(40).skip(20) {
            assert_eq!(batch_results[i].name, "batch_metric_b");
            assert_eq!(batch_results[i].step, Some((i - 20) as i32));
        }
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
    async fn test_postgres_get_load_card_key_service() {
        let client = db_client().await;
        let service_card = ServiceCardRecord::default();
        let card = ServerCard::Service(Box::new(service_card.clone()));

        client
            .card
            .insert_card(&CardTable::Service, &card)
            .await
            .unwrap();
        let encrypted_key: Vec<u8> = (0..32).collect();
        let key = ArtifactKey {
            uid: service_card.uid.clone(),
            space: "repo1".to_string(),
            registry_type: RegistryType::Service,
            encrypted_key: encrypted_key.clone(),
            storage_key: "opsml_registry".to_string(),
        };

        client.artifact.insert_artifact_key(&key).await.unwrap();

        // test uid (testing to ensure it doesnt fail)
        let _key = client
            .card
            .get_card_key_for_loading(
                &CardTable::Service,
                &CardQueryArgs {
                    uid: Some(service_card.uid.clone()),
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
                &CardTable::Service,
                &CardQueryArgs {
                    space: Some(service_card.space.clone()),
                    name: Some(service_card.name.clone()),
                    version: Some(service_card.version.to_string()),
                    ..Default::default()
                },
            )
            .await
            .unwrap();

        let _ = client
            .artifact
            .get_artifact_key_from_path(&key.storage_key, &RegistryType::Service.to_string())
            .await
            .unwrap()
            .unwrap();

        assert_eq!(key.uid, service_card.uid);
        assert_eq!(key.encrypted_key, encrypted_key);

        // delete
        client
            .artifact
            .delete_artifact_key(&service_card.uid, &RegistryType::Service.to_string())
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
            EvaluationType::GenAI,
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
        let service1 = ServiceCardRecord {
            name: "Service1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Api.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            ..Default::default()
        };
        client
            .card
            .insert_card(
                &CardTable::Service,
                &ServerCard::Service(Box::new(service1)),
            )
            .await
            .unwrap();

        // create 2nd card
        let service2 = ServiceCardRecord {
            name: "Service2".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Api.to_string(),
            ..Default::default()
        };
        client
            .card
            .insert_card(
                &CardTable::Service,
                &ServerCard::Service(Box::new(service2)),
            )
            .await
            .unwrap();

        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: None,
                service_type: ServiceType::Api,
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
                service_type: ServiceType::Api,
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 1);
    }

    #[tokio::test]
    async fn test_postgres_recent_mcp_services() {
        let client = db_client().await;

        // create 1st service card
        let mcp1 = ServiceCardRecord {
            name: "mcp1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Mcp.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            ..Default::default()
        };
        client
            .card
            .insert_card(&CardTable::Mcp, &ServerCard::Service(Box::new(mcp1)))
            .await
            .unwrap();

        // create 2nd card
        let mcp2 = ServiceCardRecord {
            name: "mcp2".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Mcp.to_string(),
            ..Default::default()
        };
        client
            .card
            .insert_card(&CardTable::Mcp, &ServerCard::Service(Box::new(mcp2)))
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
            urls: vec!["http://localhost:8000".to_string()],
            resources: Some(Resources {
                cpu: 2,
                memory: "4GB".to_string(),
                storage: "10GB".to_string(),
                gpu: None,
            }),
            links: None,
            healthcheck: Some("/health".to_string()),
        };
        let mcp3 = ServiceCardRecord {
            name: "mcp1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Mcp.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            service_config: Some(Json(ServiceConfig {
                mcp: Some(mcp_config),
                ..Default::default()
            })),
            deployment: Some(Json(vec![deploy])),
            ..Default::default()
        };

        // wait 1 second to ensure different created_at timestamp
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        client
            .card
            .insert_card(&CardTable::Mcp, &ServerCard::Service(Box::new(mcp3)))
            .await
            .unwrap();

        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: None,
                service_type: ServiceType::Mcp,
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
                service_type: ServiceType::Mcp,
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 1);

        // check that endpoint is populated
        assert!(services[0].deployment.is_some());
        let deployment = services[0].deployment.as_ref().unwrap();
        assert_eq!(deployment.len(), 1);
        assert_eq!(deployment[0].environment, "dev");
        assert_eq!(deployment[0].urls.len(), 1);
        assert_eq!(deployment[0].urls[0], "http://localhost:8000");
        assert_eq!(deployment[0].healthcheck.as_deref(), Some("/health"));
    }

    #[tokio::test]
    async fn test_postgres_recent_agent_services() {
        let client = db_client().await;
        let agent_spec = example_agent_spec();

        let deploy = DeploymentConfig {
            environment: "dev".to_string(),
            provider: Some("development".to_string()),
            location: Some(vec!["local".to_string()]),
            urls: vec!["http://localhost:8000".to_string()],
            resources: Some(Resources {
                cpu: 2,
                memory: "4GB".to_string(),
                storage: "10GB".to_string(),
                gpu: None,
            }),
            links: None,
            healthcheck: Some("/health".to_string()),
        };
        let agent_card1 = ServiceCardRecord {
            name: "agent1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Agent.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            service_config: Some(Json(ServiceConfig {
                agent: Some(opsml_types::contracts::AgentConfig::Spec(Box::new(
                    agent_spec.clone(),
                ))),
                ..Default::default()
            })),
            deployment: Some(Json(vec![deploy.clone()])),
            ..Default::default()
        };

        client
            .card
            .insert_card(
                &CardTable::Agent,
                &ServerCard::Service(Box::new(agent_card1)),
            )
            .await
            .unwrap();

        tokio::time::sleep(std::time::Duration::from_millis(300)).await;

        // create new version
        let agent_card2 = ServiceCardRecord {
            name: "agent1".to_string(),
            space: SPACE.to_string(),
            service_type: ServiceType::Agent.to_string(),
            tags: Json(vec!["tag1".to_string()]),
            service_config: Some(Json(ServiceConfig {
                agent: Some(opsml_types::contracts::AgentConfig::Spec(Box::new(
                    agent_spec.clone(),
                ))),
                ..Default::default()
            })),
            deployment: Some(Json(vec![deploy])),
            ..Default::default()
        };

        client
            .card
            .insert_card(
                &CardTable::Agent,
                &ServerCard::Service(Box::new(agent_card2)),
            )
            .await
            .unwrap();

        let services = client
            .card
            .get_recent_services(&ServiceQueryArgs {
                space: None,
                name: None,
                tags: None,
                service_type: ServiceType::Agent,
            })
            .await
            .unwrap();
        assert_eq!(services.len(), 1);

        // check that endpoint is populated
        assert!(services[0].deployment.is_some());
        let deployment = services[0].deployment.as_ref().unwrap();
        assert_eq!(deployment.len(), 1);
        assert_eq!(deployment[0].environment, "dev");
        assert_eq!(deployment[0].urls.len(), 1);
        assert_eq!(deployment[0].urls[0], "http://localhost:8000");
        assert_eq!(deployment[0].healthcheck.as_deref(), Some("/health"));
    }
}
