use crate::{postgres::helper::PostgresQueryHelper, traits::ArtifactLogicTrait};

use crate::error::SqlError;

use crate::schemas::ArtifactSqlRecord;
use async_trait::async_trait;
use opsml_types::{
    contracts::{ArtifactKey, ArtifactQueryArgs, ArtifactRecord},
    RegistryType,
};
use sqlx::{Pool, Postgres};

#[derive(Debug, Clone)]
pub struct ArtifactLogicPostgresClient {
    pool: sqlx::Pool<Postgres>,
}
impl ArtifactLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl ArtifactLogicTrait for ArtifactLogicPostgresClient {
    async fn query_artifacts(
        &self,
        query_args: &ArtifactQueryArgs,
    ) -> Result<Vec<ArtifactRecord>, SqlError> {
        let query = PostgresQueryHelper::get_query_artifacts_query(query_args)?;
        let rows: Vec<ArtifactSqlRecord> = sqlx::query_as(&query)
            .bind(query_args.uid.as_ref())
            .bind(query_args.artifact_type.as_ref().map(|a| a.to_string()))
            .bind(query_args.space.as_ref())
            .bind(query_args.name.as_ref())
            .bind(query_args.limit.unwrap_or(50))
            .fetch_all(&self.pool)
            .await?;

        Ok(rows
            .iter()
            .map(|r| r.to_artifact_record())
            .collect::<Vec<ArtifactRecord>>())
    }

    async fn insert_artifact_record(&self, record: &ArtifactSqlRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_record_insert_query();
        sqlx::query(&query)
            .bind(&record.uid)
            .bind(record.created_at)
            .bind(&record.app_env)
            .bind(&record.space)
            .bind(&record.name)
            .bind(record.major)
            .bind(record.minor)
            .bind(record.patch)
            .bind(&record.pre_tag)
            .bind(&record.build_tag)
            .bind(&record.version)
            .bind(&record.media_type)
            .bind(&record.artifact_type)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_insert_query();

        sqlx::query(&query)
            .bind(&key.uid)
            .bind(&key.space)
            .bind(key.registry_type.to_string())
            .bind(key.encrypted_key.clone())
            .bind(&key.storage_key)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_artifact_key(
        &self,
        uid: &str,
        registry_type: &str,
    ) -> Result<ArtifactKey, SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_select_query();

        let key: (String, String, String, Vec<u8>, String) = sqlx::query_as(&query)
            .bind(uid)
            .bind(registry_type)
            .fetch_one(&self.pool)
            .await?;

        Ok(ArtifactKey {
            uid: key.0,
            space: key.1,
            registry_type: RegistryType::from_string(&key.2)?,
            encrypted_key: key.3,
            storage_key: key.4,
        })
    }

    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_from_storage_path_query();

        let key: Option<(String, String, String, Vec<u8>, String)> = sqlx::query_as(&query)
            .bind(storage_path)
            .bind(registry_type)
            .fetch_optional(&self.pool)
            .await?;

        return match key {
            Some(k) => Ok(Some(ArtifactKey {
                uid: k.0,
                space: k.1,
                registry_type: RegistryType::from_string(&k.2)?,
                encrypted_key: k.3,
                storage_key: k.4,
            })),
            None => Ok(None),
        };
    }

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_update_query();
        sqlx::query(&query)
            .bind(key.encrypted_key.clone())
            .bind(&key.uid)
            .bind(key.registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_artifact_key_delete_query();
        sqlx::query(&query)
            .bind(uid)
            .bind(registry_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
