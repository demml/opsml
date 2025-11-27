use crate::error::RegistryError;
use opsml_crypt::{derive_encryption_key, encrypted_key, generate_salt};
use opsml_semver::{error::VersionError, VersionArgs, VersionType, VersionValidator};
use opsml_settings::DatabaseSettings;
use opsml_settings::OpsmlStorageSettings;
use opsml_sql::enums::client::get_sql_client;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::*;
use opsml_sql::traits::ArtifactLogicTrait;
use opsml_sql::traits::CardLogicTrait;
use opsml_storage::StorageClientEnum;
use opsml_types::IntegratedService;
use opsml_types::RegistryMode;
use opsml_types::{cards::CardTable, contracts::*, RegistryType};
use opsml_utils::uid_to_byte_key;
use scouter_client::{ProfileRequest, ProfileStatusRequest, ScouterClient};
use semver::Version;
use sqlx::types::Json as SqlxJson;
use std::sync::Arc;
use tracing::{error, info, instrument};

#[derive(Debug, Clone)]
pub struct ServerCardRegistry {
    sql_client: Arc<SqlClientEnum>,
    pub scouter_client: Option<ScouterClient>,
    pub registry_type: RegistryType,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerCardRegistry {
    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    pub fn table_name(&self) -> String {
        CardTable::from_registry_type(&self.registry_type).to_string()
    }
    pub async fn new(
        registry_type: RegistryType,
        storage_settings: OpsmlStorageSettings,
        database_settings: DatabaseSettings,
        scouter_client: Option<ScouterClient>,
    ) -> Result<Self, RegistryError> {
        let sql_client = Arc::new(get_sql_client(&database_settings).await?);
        let table_name = CardTable::from_registry_type(&registry_type);

        Ok(Self {
            sql_client,
            table_name,
            registry_type,
            storage_settings,
            scouter_client,
        })
    }

    /// List cards from the registry
    pub async fn list_cards(&self, args: &CardQueryArgs) -> Result<Vec<CardRecord>, RegistryError> {
        let cards = self.sql_client.query_cards(&self.table_name, args).await?;

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
            CardResults::Prompt(data) => {
                let cards = data.into_iter().map(convert_promptcard).collect();
                Ok(cards)
            }
            CardResults::Service(data) => {
                let cards = data.into_iter().map(convert_servicecard).collect();
                Ok(cards)
            }
        }
    }

    /// Create a new card in the registry
    pub async fn create_card(
        &self,
        card: CardRecord,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        let version = self
            .get_next_version(
                card.space(),
                card.name(),
                version,
                version_type,
                pre_tag,
                build_tag,
            )
            .await?;

        let card = match card {
            CardRecord::Data(client_card) => {
                let server_card = DataCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.tags,
                    client_card.data_type,
                    client_card.experimentcard_uid,
                    client_card.auditcard_uid,
                    client_card.interface_type.to_string(),
                    client_card.opsml_version,
                    client_card.username,
                );
                ServerCard::Data(server_card)
            }
            CardRecord::Model(client_card) => {
                let server_card = ModelCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.tags,
                    client_card.datacard_uid,
                    client_card.data_type,
                    client_card.model_type,
                    client_card.experimentcard_uid,
                    client_card.auditcard_uid,
                    client_card.interface_type,
                    client_card.task_type,
                    client_card.opsml_version,
                    client_card.username,
                );
                ServerCard::Model(server_card)
            }

            CardRecord::Experiment(client_card) => {
                let server_card = ExperimentCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.tags,
                    client_card.datacard_uids,
                    client_card.modelcard_uids,
                    client_card.promptcard_uids,
                    client_card.service_card_uids,
                    client_card.experimentcard_uids,
                    client_card.opsml_version,
                    client_card.username,
                    client_card.status,
                );
                ServerCard::Experiment(server_card)
            }

            CardRecord::Audit(client_card) => {
                let server_card = AuditCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.tags,
                    client_card.approved,
                    client_card.datacard_uids,
                    client_card.modelcard_uids,
                    client_card.experimentcard_uids,
                    client_card.opsml_version,
                    client_card.username,
                );
                ServerCard::Audit(server_card)
            }
            CardRecord::Prompt(client_card) => {
                let server_card = PromptCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.tags,
                    client_card.experimentcard_uid,
                    client_card.auditcard_uid,
                    client_card.opsml_version,
                    client_card.username,
                );
                ServerCard::Prompt(server_card)
            }

            CardRecord::Service(client_card) => {
                let server_card = ServiceCardRecord::new(
                    client_card.name,
                    client_card.space,
                    version,
                    client_card.cards,
                    client_card.opsml_version,
                    client_card.service_type,
                    client_card.metadata,
                    client_card.deployment,
                    client_card.service_config,
                    client_card.username,
                    client_card.tags,
                );
                ServerCard::Service(server_card)
            }
        };

        self.sql_client.insert_card(&self.table_name, &card).await?;

        let key = self
            .create_artifact_key(
                card.uid(),
                &card.space(),
                &card.registry_type(),
                &card.uri(),
            )
            .await?;

        let response = CreateCardResponse {
            registered: true,
            version: card.version(),
            space: card.space(),
            name: card.name(),
            app_env: card.app_env(),
            created_at: card.created_at(),
            key: ArtifactKey {
                uid: key.uid,
                space: key.space,
                registry_type: key.registry_type,
                encrypted_key: key.encrypted_key,
                storage_key: key.storage_key,
            },
        };
        Ok(response)
    }

    pub async fn update_card(&self, card: &CardRecord) -> Result<(), RegistryError> {
        let card = card.clone();
        let card = match card {
            CardRecord::Data(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = DataCardRecord {
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
                    tags: SqlxJson(client_card.tags),
                    data_type: client_card.data_type,
                    experimentcard_uid: client_card.experimentcard_uid,
                    auditcard_uid: client_card.auditcard_uid,
                    interface_type: client_card.interface_type,
                    username: client_card.username,
                    opsml_version: client_card.opsml_version,
                };
                ServerCard::Data(server_card)
            }

            CardRecord::Model(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = ModelCardRecord {
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
                    tags: SqlxJson(client_card.tags),
                    datacard_uid: client_card.datacard_uid,
                    data_type: client_card.data_type,
                    model_type: client_card.model_type,
                    experimentcard_uid: client_card.experimentcard_uid,
                    auditcard_uid: client_card.auditcard_uid,
                    interface_type: client_card.interface_type,
                    task_type: client_card.task_type,
                    username: client_card.username,
                    opsml_version: client_card.opsml_version,
                };
                ServerCard::Model(server_card)
            }

            CardRecord::Experiment(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = ExperimentCardRecord {
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
                    tags: SqlxJson(client_card.tags),
                    datacard_uids: SqlxJson(client_card.datacard_uids),
                    modelcard_uids: SqlxJson(client_card.modelcard_uids),
                    promptcard_uids: SqlxJson(client_card.promptcard_uids),
                    service_card_uids: SqlxJson(client_card.service_card_uids),
                    experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                    username: client_card.username,
                    opsml_version: client_card.opsml_version,
                    status: client_card.status,
                };
                ServerCard::Experiment(server_card)
            }

            CardRecord::Audit(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = AuditCardRecord {
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
                    tags: SqlxJson(client_card.tags),
                    approved: client_card.approved,
                    datacard_uids: SqlxJson(client_card.datacard_uids),
                    modelcard_uids: SqlxJson(client_card.modelcard_uids),
                    experimentcard_uids: SqlxJson(client_card.experimentcard_uids),
                    username: client_card.username,
                    opsml_version: client_card.opsml_version,
                };
                ServerCard::Audit(server_card)
            }

            CardRecord::Prompt(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = PromptCardRecord {
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
                    tags: SqlxJson(client_card.tags),
                    experimentcard_uid: client_card.experimentcard_uid,
                    auditcard_uid: client_card.auditcard_uid,
                    username: client_card.username,
                    opsml_version: client_card.opsml_version,
                };
                ServerCard::Prompt(server_card)
            }

            CardRecord::Service(client_card) => {
                let version =
                    Version::parse(&client_card.version).map_err(VersionError::InvalidVersion)?;

                let server_card = ServiceCardRecord {
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
                    cards: SqlxJson(client_card.cards),
                    username: client_card.username,
                    service_type: client_card.service_type,
                    metadata: client_card.metadata.map(SqlxJson),
                    deployment: client_card.deployment.map(SqlxJson),
                    service_config: client_card.service_config.map(SqlxJson),
                    tags: SqlxJson(client_card.tags),
                    opsml_version: client_card.opsml_version,
                };
                ServerCard::Service(server_card)
            }
        };

        self.sql_client.update_card(&self.table_name, &card).await?;

        Ok(())
    }

    #[instrument(skip_all)]
    pub async fn delete_card(
        &self,
        delete_request: DeleteCardRequest,
    ) -> Result<(), RegistryError> {
        let args = CardQueryArgs {
            uid: Some(delete_request.uid.to_string()),
            registry_type: delete_request.registry_type.clone(),
            ..Default::default()
        };
        // get key
        let key = self.get_key(&args).await.inspect_err(|e| {
            error!("Error getting key for delete request: {}", e);
        })?;

        // get storage client and delete artifacts
        let storage_client = StorageClientEnum::new(&self.storage_settings).await?;

        // Delete saved artifacts if they exist
        if storage_client.find(&key.storage_path()).await?.is_empty() {
            info!("No files found at storage path. Skipping artifact deletion");
        } else {
            storage_client.rm(&key.storage_path(), true).await?;
        }

        // Delete the artifact key
        self.sql_client
            .delete_artifact_key(&delete_request.uid, &key.registry_type.to_string())
            .await?;

        // Delete the card from registry
        self.sql_client
            .delete_card(&self.table_name, &delete_request.uid)
            .await?;

        Ok(())
    }

    pub async fn get_key(&self, args: &CardQueryArgs) -> Result<ArtifactKey, RegistryError> {
        let table = CardTable::from_registry_type(&args.registry_type);
        Ok(self
            .sql_client
            .get_card_key_for_loading(&table, args)
            .await?)
    }

    pub async fn check_uid_exists(&self, uid: &str) -> Result<bool, RegistryError> {
        Ok(self
            .sql_client
            .check_uid_exists(uid, &self.table_name)
            .await?)
    }

    pub async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        let key = self
            .sql_client
            .get_artifact_key(uid, &registry_type.to_string())
            .await?;

        Ok(key)
    }

    async fn get_next_version(
        &self,
        space: &str,
        name: &str,
        version: Option<String>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<Version, RegistryError> {
        let versions = self
            .sql_client
            .get_versions(&self.table_name, space, name, version.clone())
            .await?;

        // if no versions exist, return the default version
        if versions.is_empty() {
            return match &version {
                Some(version_str) => Ok(VersionValidator::clean_version(version_str)?),
                None => Ok(Version::new(0, 1, 0)),
            };
        }

        let base_version = versions.first().unwrap().to_string();

        let args = VersionArgs {
            version: base_version,
            version_type,
            pre: pre_tag,
            build: build_tag,
        };

        Ok(VersionValidator::bump_version(&args)?)
    }

    async fn create_artifact_key(
        &self,
        uid: &str,
        space: &str,
        registry_type: &str,
        storage_key: &str,
    ) -> Result<ArtifactKey, RegistryError> {
        let salt = generate_salt()?;

        let derived_key = derive_encryption_key(
            &self.storage_settings.encryption_key,
            &salt,
            registry_type.as_bytes(),
        )?;

        let uid_key = uid_to_byte_key(uid)?;

        let encrypted_key = encrypted_key(&uid_key, &derived_key)?;

        let artifact_key = ArtifactKey {
            uid: uid.to_string(),
            space: space.to_string(),
            registry_type: RegistryType::from_string(registry_type)?,
            encrypted_key,
            storage_key: storage_key.to_string(),
        };

        self.sql_client.insert_artifact_key(&artifact_key).await?;

        Ok(artifact_key)
    }

    pub fn check_service_health(&self, service: IntegratedService) -> Result<bool, RegistryError> {
        match service {
            IntegratedService::Scouter => {
                // check if scouter client is initialized. If not, return false
                if self.scouter_client.is_none() {
                    return Ok(false);
                }
                // if scouter client is initialized, check service health
                let client = self
                    .scouter_client
                    .as_ref()
                    .ok_or(RegistryError::ScouterClientNotFoundError)?;
                Ok(client.check_service_health()?)
            }
        }
    }

    pub fn insert_scouter_profile(&self, request: &ProfileRequest) -> Result<(), RegistryError> {
        let client = self
            .scouter_client
            .as_ref()
            .ok_or(RegistryError::ScouterClientNotFoundError)?;
        client.insert_profile(request)?;
        Ok(())
    }

    pub fn update_drift_profile_status(
        &self,
        request: &ProfileStatusRequest,
    ) -> Result<(), RegistryError> {
        let client = self
            .scouter_client
            .as_ref()
            .ok_or(RegistryError::ScouterClientNotFoundError)?;
        client.update_profile_status(request)?;
        Ok(())
    }
}
