use crate::error::RegistryError;
use opsml_settings::config::OpsmlStorageSettings;

use opsml_sql::{
    enums::client::SqlClientEnum, enums::utils::get_next_version, schemas::*, traits::*,
};

use opsml_types::{cards::CardTable, contracts::*, *};

use std::sync::Arc;

pub struct ServerArtifactRegistry {
    sql_client: Arc<SqlClientEnum>,
    pub registry_type: RegistryType,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerArtifactRegistry {
    pub async fn new(
        sql_client: Arc<SqlClientEnum>,
        registry_type: RegistryType,
        table_name: CardTable,
        storage_settings: OpsmlStorageSettings,
    ) -> Self {
        Self {
            sql_client,

            registry_type,
            table_name,
            storage_settings,
        }
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
