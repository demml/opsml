use crate::{sqlite::helper::SqliteQueryHelper, traits::SpaceLogicTrait};

use crate::error::SqlError;

use crate::schemas::SqlSpaceRecord;
use async_trait::async_trait;
use opsml_types::{
    contracts::{SpaceNameEvent, SpaceRecord, SpaceStats},
    RegistryType,
};
use sqlx::{Pool, Sqlite};

#[derive(Debug)]
pub struct SpaceLogicSqliteClient {
    pool: sqlx::Pool<Sqlite>,
}
impl SpaceLogicSqliteClient {
    pub fn new(pool: &Pool<Sqlite>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl SpaceLogicTrait for SpaceLogicSqliteClient {
    async fn insert_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_insert_space_record_query();
        sqlx::query(&query)
            .bind(&space.space)
            .bind(&space.description)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
    async fn insert_space_name_record(&self, event: &SpaceNameEvent) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_insert_space_name_record_query();
        sqlx::query(&query)
            .bind(&event.space)
            .bind(&event.name)
            .bind(event.registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_all_space_stats(&self) -> Result<Vec<SpaceStats>, SqlError> {
        let query = SqliteQueryHelper::get_all_space_stats_query();
        let spaces: Vec<SqlSpaceRecord> = sqlx::query_as(&query).fetch_all(&self.pool).await?;

        Ok(spaces
            .into_iter()
            .map(|s| SpaceStats {
                space: s.0,
                model_count: s.1,
                data_count: s.2,
                prompt_count: s.3,
                experiment_count: s.4,
            })
            .collect())
    }

    async fn get_space_record(&self, space: &str) -> Result<Option<SpaceRecord>, SqlError> {
        let query = SqliteQueryHelper::get_space_record_query();
        let record: Option<(String, String)> = sqlx::query_as(&query)
            .bind(space)
            .fetch_optional(&self.pool)
            .await?;

        Ok(record.map(|r| SpaceRecord {
            space: r.0,
            description: r.1,
        }))
    }

    async fn update_space_record(&self, space: &SpaceRecord) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_update_space_record_query();
        sqlx::query(&query)
            .bind(&space.description)
            .bind(&space.space)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn delete_space_record(&self, space: &str) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_delete_space_record_query();
        sqlx::query(&query).bind(space).execute(&self.pool).await?;

        Ok(())
    }

    async fn delete_space_name_record(
        &self,
        space: &str,
        name: &str,
        registry_type: &RegistryType,
    ) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_delete_space_name_record_query();
        sqlx::query(&query)
            .bind(space)
            .bind(name)
            .bind(registry_type.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
