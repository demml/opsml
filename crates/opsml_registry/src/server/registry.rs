#[cfg(feature = "server")]
pub mod server_logic {
    // We implement 2 versions of the registry, one for rust compatibility and one for python compatibility

    use opsml_crypt::{decrypt_key, derive_encryption_key, encrypted_key, generate_salt};
    use opsml_error::error::RegistryError;
    use opsml_semver::{VersionArgs, VersionType, VersionValidator};
    use opsml_settings::config::DatabaseSettings;
    use opsml_settings::config::OpsmlConfig;
    use opsml_settings::config::OpsmlStorageSettings;
    use opsml_sql::{
        base::SqlClient,
        enums::client::{get_sql_client, SqlClientEnum},
        schemas::*,
    };
    use opsml_storage::StorageClientEnum;
    use opsml_types::{cards::CardTable, contracts::*, *};
    use opsml_utils::uid_to_byte_key;
    use pyo3::prelude::*;
    use semver::Version;
    use sqlx::types::Json as SqlxJson;
    use tracing::error;

    #[derive(Debug, Clone)]
    pub struct ServerRegistry {
        sql_client: SqlClientEnum,
        pub registry_type: RegistryType,
        pub table_name: CardTable,
        pub storage_settings: OpsmlStorageSettings,
    }

    impl ServerRegistry {
        pub async fn new(
            config: &OpsmlConfig,
            registry_type: RegistryType,
        ) -> Result<Self, RegistryError> {
            let sql_client = get_sql_client(config).await.map_err(|e| {
                RegistryError::NewError(format!("Failed to create sql client {}", e))
            })?;

            let table_name = CardTable::from_registry_type(&registry_type);
            Ok(Self {
                sql_client,
                table_name,
                registry_type,
                storage_settings: config.storage_settings()?,
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

                CardResults::Experiment(data) => {
                    let cards = data.into_iter().map(convert_experimentcard).collect();
                    Ok(cards)
                }

                CardResults::Audit(data) => {
                    let cards = data.into_iter().map(convert_auditcard).collect();
                    Ok(cards)
                }
            }
        }

        async fn get_next_version(
            &mut self,
            name: &str,
            repository: &str,
            version: Option<String>,
            version_type: VersionType,
            pre_tag: Option<String>,
            build_tag: Option<String>,
        ) -> Result<Version, RegistryError> {
            let versions = self
                .sql_client
                .get_versions(&self.table_name, name, repository, version)
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

        async fn create_artifact_key(
            &mut self,
            uid: &str,
            registry_type: &str,
            storage_key: &str,
        ) -> Result<ArtifactKey, RegistryError> {
            let salt = generate_salt();

            let derived_key = derive_encryption_key(
                &self.storage_settings.encryption_key,
                &salt,
                registry_type.as_bytes(),
            )?;

            let uid_key = uid_to_byte_key(uid)?;

            let encrypted_key = encrypted_key(&uid_key, &derived_key)?;

            let artifact_key = ArtifactKey {
                uid: uid.to_string(),
                registry_type: RegistryType::from_string(registry_type)?,
                encrypted_key,
                storage_key: storage_key.to_string(),
            };

            self.sql_client.insert_artifact_key(&artifact_key).await?;

            Ok(artifact_key)
        }

        pub async fn create_card(
            &mut self,
            card: Card,
            version: Option<String>,
            version_type: VersionType,
            pre_tag: Option<String>,
            build_tag: Option<String>,
        ) -> Result<CreateCardResponse, RegistryError> {
            let version = self
                .get_next_version(
                    card.name(),
                    card.repository(),
                    version,
                    version_type,
                    pre_tag,
                    build_tag,
                )
                .await?;

            let card = match card {
                Card::Data(client_card) => {
                    let server_card = DataCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        version,
                        client_card.tags,
                        client_card.data_type,
                        client_card.experimentcard_uid,
                        client_card.auditcard_uid,
                        client_card.interface_type.to_string(),
                        client_card.username,
                    );
                    ServerCard::Data(server_card)
                }
                Card::Model(client_card) => {
                    let server_card = ModelCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        version,
                        client_card.tags,
                        client_card.datacard_uid,
                        client_card.data_type,
                        client_card.model_type,
                        client_card.experimentcard_uid,
                        client_card.auditcard_uid,
                        client_card.interface_type,
                        client_card.task_type,
                        client_card.username,
                    );
                    ServerCard::Model(server_card)
                }

                Card::Experiment(client_card) => {
                    let server_card = experimentcardRecord::new(
                        client_card.name,
                        client_card.repository,
                        version,
                        client_card.tags,
                        client_card.datacard_uids,
                        client_card.modelcard_uids,
                        client_card.experimentcard_uids,
                        client_card.username,
                    );
                    ServerCard::Experiment(server_card)
                }

                Card::Audit(client_card) => {
                    let server_card = AuditCardRecord::new(
                        client_card.name,
                        client_card.repository,
                        version,
                        client_card.tags,
                        client_card.approved,
                        client_card.datacard_uids,
                        client_card.modelcard_uids,
                        client_card.experimentcard_uids,
                        client_card.username,
                    );
                    ServerCard::Audit(server_card)
                }
            };

            self.sql_client
                .insert_card(&self.table_name, &card)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to create card {}", e)))?;

            let key = self
                .create_artifact_key(card.uid(), &card.registry_type(), &card.uri())
                .await
                .map_err(|e| {
                    RegistryError::Error(format!("Failed to create artifact key {}", e))
                })?;

            let response = CreateCardResponse {
                registered: true,
                version: card.version(),
                repository: card.registry_type(),
                name: card.name(),
                app_env: card.app_env(),
                created_at: card.created_at(),
                key: ArtifactKey {
                    uid: key.uid,
                    registry_type: key.registry_type,
                    encrypted_key: key.encrypted_key,
                    storage_key: key.storage_key,
                },
            };
            Ok(response)
        }

        pub async fn update_card(&self, card: &Card) -> Result<(), RegistryError> {
            let card = card.clone();
            let card = match card {
                Card::Data(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = DataCardRecord {
                        uid: client_card.uid,
                        created_at: client_card.created_at,
                        app_env: client_card.app_env,
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        tags: SqlxJson(client_card.tags),
                        data_type: client_card.data_type,
                        experimentcard_uid: client_card.experimentcard_uid,
                        auditcard_uid: client_card.auditcard_uid,
                        interface_type: client_card.interface_type,
                        username: client_card.username,
                    };
                    ServerCard::Data(server_card)
                }

                Card::Model(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = ModelCardRecord {
                        uid: client_card.uid,
                        created_at: client_card.created_at,
                        app_env: client_card.app_env,
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        tags: SqlxJson(client_card.tags),
                        datacard_uid: client_card.datacard_uid,
                        data_type: client_card.data_type,
                        model_type: client_card.model_type,
                        experimentcard_uid: client_card.experimentcard_uid,
                        auditcard_uid: client_card.auditcard_uid,
                        interface_type: client_card.interface_type,
                        task_type: client_card.task_type,
                        username: client_card.username,
                    };
                    ServerCard::Model(server_card)
                }

                Card::Experiment(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = experimentcardRecord {
                        uid: client_card.uid,
                        created_at: client_card.created_at,
                        app_env: client_card.app_env,
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        tags: SqlxJson(client_card.tags),
                        datacard_uids: SqlxJson(client_card.datacard_uids),
                        modelcard_uids: SqlxJson(client_card.modelcard_uids),
                        experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                        username: client_card.username,
                    };
                    ServerCard::Experiment(server_card)
                }

                Card::Audit(client_card) => {
                    let version = Version::parse(&client_card.version).map_err(|e| {
                        error!("Failed to parse version: {}", e);
                        RegistryError::Error("Failed to parse version".to_string())
                    })?;

                    let server_card = AuditCardRecord {
                        uid: client_card.uid,
                        created_at: client_card.created_at,
                        app_env: client_card.app_env,
                        name: client_card.name,
                        repository: client_card.repository,
                        major: version.major as i32,
                        minor: version.minor as i32,
                        patch: version.patch as i32,
                        pre_tag: Some(version.pre.to_string()),
                        build_tag: Some(version.build.to_string()),
                        version: client_card.version,
                        tags: SqlxJson(client_card.tags),
                        approved: client_card.approved,
                        datacard_uids: SqlxJson(client_card.datacard_uids),
                        modelcard_uids: SqlxJson(client_card.modelcard_uids),
                        experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                        username: client_card.username,
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

        pub async fn delete_card(
            &mut self,
            delete_request: DeleteCardRequest,
        ) -> Result<(), RegistryError> {
            // get key
            let key = self
                .load_card(CardQueryArgs {
                    uid: Some(delete_request.uid.to_string()),
                    ..Default::default()
                })
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to load card {}", e)))?;

            // get storage client and delete artifacts
            let storage_client = StorageClientEnum::new(&self.storage_settings)
                .await
                .map_err(|e| {
                    RegistryError::Error(format!("Failed to create storage client {}", e))
                })?;

            storage_client.rm(&key.storage_path(), true).await?;

            self.sql_client
                .delete_artifact_key(&delete_request.uid, &key.registry_type.to_string())
                .await
                .map_err(|e| {
                    RegistryError::Error(format!("Failed to delete artifact key {}", e))
                })?;

            self.sql_client
                .delete_card(&self.table_name, &delete_request.uid)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to delete card {}", e)))?;

            // delete key

            Ok(())
        }

        pub async fn load_card(
            &mut self,
            args: CardQueryArgs,
        ) -> Result<ArtifactKey, RegistryError> {
            self.sql_client
                .get_card_key_for_loading(&self.table_name, &args)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to list cards {}", e)))
        }

        pub async fn check_uid_exists(&mut self, uid: &str) -> Result<bool, RegistryError> {
            self.sql_client
                .check_uid_exists(uid, &self.table_name)
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to check uid exists {}", e)))
        }

        pub async fn get_artifact_key(
            &mut self,
            uid: &str,
            registry_type: &RegistryType,
        ) -> Result<Vec<u8>, RegistryError> {
            let key = self
                .sql_client
                .get_artifact_key(uid, &registry_type.to_string())
                .await
                .map_err(|e| RegistryError::Error(format!("Failed to get artifact key {}", e)))?;

            let uid_key = uid_to_byte_key(uid)?;

            let decrypted_key = decrypt_key(&uid_key, &key.encrypted_key)?;

            Ok(decrypted_key)
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
                    ..Default::default()
                };
                let cards = client
                    .query_cards(&CardTable::Data, &query_args)
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
