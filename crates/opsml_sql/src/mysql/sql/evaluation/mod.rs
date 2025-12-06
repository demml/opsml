use crate::schemas::EvaluationSqlRecord;
use crate::{mysql::helper::MySqlQueryHelper, traits::EvaluationLogicTrait};

use crate::error::SqlError;
use async_trait::async_trait;
use sqlx::{MySql, Pool};

#[derive(Debug, Clone)]
pub struct EvaluationLogicMySqlClient {
    pool: sqlx::Pool<MySql>,
}
impl EvaluationLogicMySqlClient {
    pub fn new(pool: &Pool<MySql>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl EvaluationLogicTrait for EvaluationLogicMySqlClient {
    async fn insert_evaluation_record(&self, event: EvaluationSqlRecord) -> Result<(), SqlError> {
        let query = MySqlQueryHelper::get_evaluation_record_insert_query();
        sqlx::query(query)
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
        let query = MySqlQueryHelper::get_evaluation_record_query();
        let record: EvaluationSqlRecord = sqlx::query_as(query)
            .bind(uid)
            .fetch_one(&self.pool)
            .await?;

        Ok(record)
    }
}
