use crate::schemas::EvaluationSqlRecord;
use crate::{sqlite::helper::SqliteQueryHelper, traits::EvaluationLogicTrait};

use crate::error::SqlError;
use async_trait::async_trait;
use sqlx::{Pool, Sqlite};

#[derive(Debug, Clone)]
pub struct EvaluationLogicSqliteClient {
    pool: sqlx::Pool<Sqlite>,
}
impl EvaluationLogicSqliteClient {
    pub fn new(pool: &Pool<Sqlite>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl EvaluationLogicTrait for EvaluationLogicSqliteClient {
    async fn insert_evaluation_record(&self, event: EvaluationSqlRecord) -> Result<(), SqlError> {
        let query = SqliteQueryHelper::get_evaluation_record_insert_query();
        sqlx::query(&query)
            .bind(event.uid)
            .bind(&event.app_env)
            .bind(&event.name)
            .bind(event.evaluation_type.to_string())
            .bind(event.evaluation_provider.to_string())
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_evaluation_record(&self, uid: &str) -> Result<EvaluationSqlRecord, SqlError> {
        let query = SqliteQueryHelper::get_evaluation_record_query();
        let record: EvaluationSqlRecord = sqlx::query_as(&query)
            .bind(uid)
            .fetch_one(&self.pool)
            .await?;

        Ok(record)
    }
}
