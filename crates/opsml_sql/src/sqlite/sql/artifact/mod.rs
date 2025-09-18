use crate::{sqlite::helper::SqliteQueryHelper, traits::ArtifactLogicTrait};

use crate::error::SqlError;

use async_trait::async_trait;
use opsml_types::{contracts::ArtifactKey, RegistryType};
use sqlx::{Pool, Sqlite};

#[derive(Debug)]
pub struct ArtifactLogicSqliteClient {
    pool: sqlx::Pool<Sqlite>,
}
impl ArtifactLogicSqliteClient {
    pub fn new(pool: &Pool<Sqlite>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl ArtifactLogicTrait for ArtifactLogicSqliteClient {
    async fn insert_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_insert_query();
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
        let query = SqliteQueryHelper::get_artifact_key_select_query();

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

    async fn update_artifact_key(&self, key: &ArtifactKey) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_update_query();
        sqlx::query(&query)
            .bind(key.encrypted_key.clone())
            .bind(&key.uid)
            .bind(key.registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }
    async fn get_artifact_key_from_path(
        &self,
        storage_path: &str,
        registry_type: &str,
    ) -> Result<Option<ArtifactKey>, SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_from_storage_path_query();

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

    async fn delete_artifact_key(&self, uid: &str, registry_type: &str) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_artifact_key_delete_query();
        sqlx::query(&query)
            .bind(uid)
            .bind(registry_type)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
