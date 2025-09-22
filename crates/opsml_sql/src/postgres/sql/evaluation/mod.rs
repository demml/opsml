use crate::schemas::EvaluationSqlRecord;
use crate::{postgres::helper::PostgresQueryHelper, traits::EvaluationLogicTrait};

use crate::error::SqlError;
use async_trait::async_trait;
use sqlx::{Pool, Postgres};

#[derive(Debug, Clone)]
pub struct EvaluationLogicPostgresClient {
    pool: sqlx::Pool<Postgres>,
}
impl EvaluationLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl EvaluationLogicTrait for EvaluationLogicPostgresClient {
    async fn insert_evaluation_record(&self, event: EvaluationSqlRecord) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_evaluation_record_insert_query();
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
        let query = PostgresQueryHelper::get_evaluation_record_query();
        let record: EvaluationSqlRecord = sqlx::query_as(&query)
            .bind(uid)
            .fetch_one(&self.pool)
            .await?;

        Ok(record)
    }
}
