use crate::error::RegistryError;
use opsml_settings::DatabaseSettings;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_sql::enums::client::get_sql_client;
use opsml_sql::enums::utils::get_next_version;
use opsml_sql::{enums::client::SqlClientEnum, schemas::*, traits::*};
use opsml_types::{cards::CardTable, contracts::*, *};
use std::sync::Arc;
#[derive(Debug)]
pub struct ServerArtifactRegistry {
    sql_client: Arc<SqlClientEnum>,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerArtifactRegistry {
    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    pub fn table_name(&self) -> String {
        self.table_name.to_string()
    }
    pub async fn new(
        storage_settings: OpsmlStorageSettings,
        database_settings: DatabaseSettings,
    ) -> Result<Self, RegistryError> {
        let sql_client = Arc::new(get_sql_client(&database_settings).await?);
        let table_name = CardTable::from_registry_type(&RegistryType::Artifact);

        Ok(Self {
            sql_client,
            table_name,
            storage_settings,
        })
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

    pub async fn log_artifact(
        &self,
        space: String,
        name: String,
        version: String,
        media_type: String,
        artifact_type: ArtifactType,
    ) -> Result<CreateArtifactResponse, RegistryError> {
        let version_request = CardVersionRequest {
            space: space.clone(),
            name: name.clone(),
            version: Some(version.clone()),
            pre_tag: None,
            build_tag: None,
            version_type: opsml_semver::VersionType::Major,
        };

        let version = get_next_version(
            self.sql_client.clone(),
            &CardTable::Artifact,
            version_request,
        )
        .await?;

        let artifact_record =
            ArtifactSqlRecord::new(space, name, version, media_type, artifact_type.to_string());

        self.sql_client
            .insert_artifact_record(&artifact_record)
            .await?;

        let response = CreateArtifactResponse {
            uid: artifact_record.uid.clone(),
            space: artifact_record.space,
            name: artifact_record.name,
            version: artifact_record.version,
        };

        Ok(response)
    }

    pub async fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, RegistryError> {
        let records = self.sql_client.query_artifacts(&query_args).await?;
        Ok(records)
    }
}
