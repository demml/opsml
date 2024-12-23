#[cfg(feature = "server")]
pub mod server_logic {
    // We implement 2 versions of the registry, one for rust compatibility and one for python compatibility

    use opsml_error::error::RegistryError;
    use opsml_settings::config::DatabaseSettings;
    use opsml_settings::config::OpsmlConfig;
    use opsml_sql::{
        base::SqlClient,
        enums::client::{get_sql_client, SqlClientEnum},
        schemas::*,
    };
    use opsml_types::*;
    use opsml_utils::{VersionArgs, VersionValidator};
    use pyo3::prelude::*;
    use semver::Version;
    use sqlx::types::Json as SqlxJson;
    use tracing::error;

    #[derive(Debug)]
    pub struct ServerRegistry {
        sql_client: SqlClientEnum,
        pub registry_type: RegistryType,
        pub table_name: CardSQLTableNames,
    }

    impl ServerRegistry {
        pub async fn new(
            config: &OpsmlConfig,
            registry_type: RegistryType,
        ) -> Result<Self, RegistryError> {
            let sql_client = get_sql_client(config).await.map_err(|e| {
                RegistryError::NewError(format!("Failed to create sql client {}", e))
            })?;

            let table_name = CardSQLTableNames::from_registry_type(&registry_type);
            Ok(Self {
                sql_client,
                table_name,
                registry_type,
            })
        }

        pub fn mode(&self) -> RegistryMode {
            RegistryMode::Server
        }

        pub fn table_name(&self) -> String {
            self.table_name.to_string()
        }

        pub async fn list_cards(
            &mut self,
            args: CardQueryArgs,
        ) -> Result<Vec<Card>, RegistryError> {
            let cards = self
                .sql_client
                .query_cards(&self.table_name, &args)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to list cards {}", e)))?;

            match cards {
                CardResults::Data(data) => {
                    let cards = data.into_iter().map(convert_datacard).collect();
                    Ok(cards)
                }
                CardResults::Model(data) => {
                    let cards = data.into_iter().map(convert_modelcard).collect();
                    Ok(cards)
                }
                CardResults::Project(data) => {
                    let cards = data.into_iter().map(convert_projectcard).collect();
                    Ok(cards)
                }
                CardResults::Run(data) => {
                    let cards = data.into_iter().map(convert_runcard).collect();
                    Ok(cards)
                }
                CardResults::Pipeline(data) => {
                    let cards = data.into_iter().map(convert_pipelinecard).collect();
                    Ok(cards)
                }
                CardResults::Audit(data) => {
                    let cards = data.into_iter().map(convert_auditcard).collect();
                    Ok(cards)
                }
            }
        }

        pub async fn create_card(&self, card: Card) -> Result<(), RegistryError> {
            let card = match card {
                Card::Data(client_card) => {
                    let server_card = DataCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.contact,
                        client_card.tags,
                        client_card.data_type,
                        client_card.runcard_uid,
                        client_card.pipelinecard_uid,
                        client_card.auditcard_uid,
                        client_card.interface_type,
                    );
                    ServerCard::Data(server_card)
                }
                Card::Model(client_card) => {
                    let server_card = ModelCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.contact,
                        client_card.tags,
                        client_card.datacard_uid,
                        client_card.sample_data_type,
                        client_card.model_type,
                        client_card.runcard_uid,
                        client_card.pipelinecard_uid,
                        client_card.auditcard_uid,
                        client_card.interface_type,
                        client_card.task_type,
                    );
                    ServerCard::Model(server_card)
                }

                Card::Project(client_card) => {
                    let server_card = ProjectCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.project_id,
                    );
                    ServerCard::Project(server_card)
                }

                Card::Run(client_card) => {
                    let server_card = RunCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.contact,
                        client_card.tags,
                        client_card.datacard_uids,
                        client_card.modelcard_uids,
                        client_card.pipelinecard_uid,
                        client_card.project,
                        client_card.artifact_uris,
                        client_card.compute_environment,
                    );
                    ServerCard::Run(server_card)
                }

                Card::Pipeline(client_card) => {
                    let server_card = PipelineCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.contact,
                        client_card.tags,
                        client_card.pipeline_code_uri,
                        client_card.datacard_uids,
                        client_card.modelcard_uids,
                        client_card.runcard_uids,
                    );
                    ServerCard::Pipeline(server_card)
                }

                Card::Audit(client_card) => {
                    let server_card = AuditCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        client_card.version.parse().unwrap(),
                        client_card.contact,
                        client_card.tags,
                        client_card.approved,
                        client_card.datacard_uids,
                        client_card.modelcard_uids,
                        client_card.runcard_uids,
                    );
                    ServerCard::Audit(server_card)
                }
            };

            self.sql_client
                .insert_card(&self.table_name, &card)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to create card {}", e)))?;

            Ok(())
        }

        pub async fn update_card(&self, card: Card) -> Result<(), RegistryError> {
            let card = match card {
                Card::Data(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = DataCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        app_env: client_card.app_env.unwrap(),
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        contact: client_card.contact,
                        tags: SqlxJson(client_card.tags),
                        data_type: client_card.data_type,
                        runcard_uid: client_card.runcard_uid.unwrap(),
                        pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                        auditcard_uid: client_card.auditcard_uid.unwrap(),
                        interface_type: client_card.interface_type.unwrap(),
                    };
                    ServerCard::Data(server_card)
                }

                Card::Model(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = ModelCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        app_env: client_card.app_env.unwrap(),
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        contact: client_card.contact,
                        tags: SqlxJson(client_card.tags),
                        datacard_uid: client_card.datacard_uid.unwrap(),
                        sample_data_type: client_card.sample_data_type,
                        model_type: client_card.model_type,
                        runcard_uid: client_card.runcard_uid.unwrap(),
                        pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                        auditcard_uid: client_card.auditcard_uid.unwrap(),
                        interface_type: client_card.interface_type.unwrap(),
                        task_type: client_card.task_type.unwrap(),
                    };
                    ServerCard::Model(server_card)
                }

                Card::Project(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = ProjectCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        project_id: client_card.project_id,
                    };
                    ServerCard::Project(server_card)
                }

                Card::Run(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = RunCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        app_env: client_card.app_env.unwrap(),
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        contact: client_card.contact,
                        tags: SqlxJson(client_card.tags),
                        datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                        modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                        pipelinecard_uid: client_card.pipelinecard_uid.unwrap(),
                        project: client_card.project,
                        artifact_uris: SqlxJson(client_card.artifact_uris.unwrap()),
                        compute_environment: SqlxJson(client_card.compute_environment.unwrap()),
                    };
                    ServerCard::Run(server_card)
                }

                Card::Pipeline(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = PipelineCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        app_env: client_card.app_env.unwrap(),
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        contact: client_card.contact,
                        tags: SqlxJson(client_card.tags),
                        pipeline_code_uri: client_card.pipeline_code_uri,
                        datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                        modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                        runcard_uids: SqlxJson(client_card.runcard_uids.unwrap()),
                    };
                    ServerCard::Pipeline(server_card)
                }

                Card::Audit(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = AuditCardRecord {
                        uid: client_card.uid.unwrap(),
                        created_at: client_card.created_at,
                        app_env: client_card.app_env.unwrap(),
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        contact: client_card.contact,
                        tags: SqlxJson(client_card.tags),
                        approved: client_card.approved,
                        datacard_uids: SqlxJson(client_card.datacard_uids.unwrap()),
                        modelcard_uids: SqlxJson(client_card.modelcard_uids.unwrap()),
                        runcard_uids: SqlxJson(client_card.runcard_uids.unwrap()),
                    };
                    ServerCard::Audit(server_card)
                }
            };

            self.sql_client
                .update_card(&self.table_name, &card)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to update card {}", e)))?;

            Ok(())
        }

        pub async fn delete_card(&self, uid: &str) -> Result<(), RegistryError> {
            self.sql_client
                .delete_card(&self.table_name, uid)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to delete card {}", e)))?;

            Ok(())
        }

        pub async fn check_uid_exists(&mut self, uid: &str) -> Result<bool, RegistryError> {
            self.sql_client
                .check_uid_exists(uid, &self.table_name)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to check uid exists {}", e)))
        }

        pub async fn get_next_version(
            &mut self,
            name: &str,
            repository: &str,
            version: Option<String>,
            version_type: VersionType,
            pre_tag: Option<String>,
            build_tag: Option<String>,
        ) -> Result<String, RegistryError> {
            let versions = self
                .sql_client
                .get_versions(&self.table_name, name, repository, version.as_deref())
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to get versions {}", e)))?;

            let version = versions.first().ok_or_else(|| {
                error!("Failed to get first version");
                RegistryError::Error("Failed to get first version".to_string())
            })?;

            let args = VersionArgs {
                version: version.to_string(),
                version_type,
                pre: pre_tag.map(|s| s.to_string()),
                build: build_tag.map(|s| s.to_string()),
            };

            let bumped_version = VersionValidator::bump_version(&args).map_err(|e| {
                error!("Failed to bump version: {}", e);
                RegistryError::Error("Failed to bump version".to_string())
            })?;

            Ok(bumped_version)
        }
    }

    #[pyclass]
    #[derive(Debug)]
    pub struct RegistryTestHelper {}

    impl RegistryTestHelper {
        fn create_registry_storage() -> String {
            let current_dir = std::env::current_dir().unwrap();
            // get 2 parents up
            let registry_path = current_dir.join("opsml_registries");

            let string_path = registry_path.to_str().unwrap().to_string();

            // create the registry folder if it does not exist
            if !registry_path.exists() {
                std::fs::create_dir(registry_path).unwrap();
            }

            string_path
        }

        fn get_connection_uri(&self) -> String {
            let current_dir = std::env::current_dir().expect("Failed to get current directory");
            let db_path = current_dir.join("opsml.db");

            format!(
                "sqlite://{}",
                db_path.to_str().expect("Failed to convert path to string")
            )
        }
    }

    impl Default for RegistryTestHelper {
        fn default() -> Self {
            Self::new()
        }
    }

    #[pymethods]
    impl RegistryTestHelper {
        #[new]
        pub fn new() -> Self {
            Self {}
        }

        pub fn setup(&self) {
            self.cleanup();

            let storage_uri = RegistryTestHelper::create_registry_storage();

            let config = DatabaseSettings {
                connection_uri: self.get_connection_uri(),
                max_connections: 1,
                sql_type: SqlType::Sqlite,
            };

            tokio::runtime::Runtime::new().unwrap().block_on(async {
                let script = include_str!("../../tests/populate_db.sql");

                let client = SqlClientEnum::new(&config).await.unwrap();

                let _ = client.query(script).await;

                // check records
                let query_args = CardQueryArgs {
                    uid: None,
                    name: None,
                    repository: None,
                    version: None,
                    max_date: None,
                    tags: None,
                    limit: None,
                    sort_by_timestamp: None,
                };
                let cards = client
                    .query_cards(&CardSQLTableNames::Data, &query_args)
                    .await
                    .unwrap();

                assert_eq!(cards.len(), 10);
            });

            // set tracking uri
            std::env::set_var("OPSML_TRACKING_URI", config.connection_uri);
            std::env::set_var("OPSML_STORAGE_URI", storage_uri);
        }

        pub fn cleanup(&self) {
            let current_dir = std::env::current_dir().unwrap();
            // get 2 parents up

            let db_path = current_dir.join("opsml.db");
            let registry_path = current_dir.join("opsml_registries");

            if db_path.exists() {
                std::fs::remove_file(db_path).unwrap();
            }

            if registry_path.exists() {
                std::fs::remove_dir_all(registry_path).unwrap();
            }

            std::env::remove_var("OPSML_TRACKING_URI");
            std::env::remove_var("OPSML_STORAGE_URI");
        }
    }
}
