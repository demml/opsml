use crate::mysql::helper::MySqlQueryHelper;
use opsml_types::cards::CardTable;

use crate::error::SqlError;
use crate::schemas::schema::{HardwareMetricsRecord, MetricRecord, ParameterRecord};

use crate::traits::ExperimentLogicTrait;
use async_trait::async_trait;
use sqlx::{MySql, Pool};

#[derive(Debug, Clone)]
pub struct ExperimentLogicMySqlClient {
    pool: sqlx::Pool<MySql>,
}
impl ExperimentLogicMySqlClient {
    pub fn new(pool: &Pool<MySql>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl ExperimentLogicTrait for ExperimentLogicMySqlClient {
    async fn insert_experiment_metric(&self, record: &MetricRecord) -> Result<(), SqlError> {
        let query = MySqlQueryHelper::get_experiment_metric_insert_query();

        sqlx::query(query)
            .bind(&record.experiment_uid)
            .bind(&record.name)
            .bind(record.value)
            .bind(record.step)
            .bind(record.timestamp)
            .bind(record.is_eval)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn insert_experiment_metrics<'life1>(
        &self,
        records: &'life1 [MetricRecord],
    ) -> Result<(), SqlError> {
        let query = MySqlQueryHelper::get_experiment_metrics_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for r in records {
            query_builder = query_builder
                .bind(&r.experiment_uid)
                .bind(&r.name)
                .bind(r.value)
                .bind(r.step)
                .bind(r.timestamp)
                .bind(r.is_eval);
        }

        query_builder.execute(&self.pool).await?;

        Ok(())
    }

    async fn get_experiment_metric<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
        is_eval: Option<bool>,
    ) -> Result<Vec<MetricRecord>, SqlError> {
        let query = MySqlQueryHelper::get_experiment_metric_query();

        // Convert names array to comma-separated string for FIND_IN_SET
        let names_csv = if names.is_empty() {
            None
        } else {
            Some(names.join(","))
        };

        let records: Vec<MetricRecord> = sqlx::query_as::<_, MetricRecord>(query)
            .bind(uid)
            .bind(names_csv.as_ref()) // NULL check
            .bind(names_csv.as_ref()) // Actual CSV value
            .bind(is_eval) // NULL check
            .bind(is_eval) // Actual boolean value
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn get_experiment_metric_names(&self, uid: &str) -> Result<Vec<String>, SqlError> {
        let query = format!(
            "SELECT DISTINCT name FROM {} WHERE experiment_uid = ?",
            CardTable::Metrics
        );

        let records: Vec<String> = sqlx::query_scalar(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }
    async fn insert_hardware_metrics(
        &self,
        record: &HardwareMetricsRecord,
    ) -> Result<(), SqlError> {
        let query = MySqlQueryHelper::get_hardware_metrics_insert_query();
        sqlx::query(query)
            .bind(&record.experiment_uid)
            .bind(record.created_at)
            .bind(record.cpu_percent_utilization)
            .bind(&record.cpu_percent_per_core)
            .bind(record.free_memory)
            .bind(record.total_memory)
            .bind(record.used_memory)
            .bind(record.available_memory)
            .bind(record.used_percent_memory)
            .bind(record.bytes_recv)
            .bind(record.bytes_sent)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    async fn get_hardware_metric(&self, uid: &str) -> Result<Vec<HardwareMetricsRecord>, SqlError> {
        let query = format!(
            "SELECT * FROM {} WHERE experiment_uid = ?",
            CardTable::HardwareMetrics
        );

        let records: Vec<HardwareMetricsRecord> = sqlx::query_as(&query)
            .bind(uid)
            .fetch_all(&self.pool)
            .await?;

        Ok(records)
    }

    async fn insert_experiment_parameters<'life1>(
        &self,
        records: &'life1 [ParameterRecord],
    ) -> Result<(), SqlError> {
        let query = MySqlQueryHelper::get_experiment_parameters_insert_query(records.len());

        let mut query_builder = sqlx::query(&query);

        for record in records {
            query_builder = query_builder
                .bind(&record.experiment_uid)
                .bind(&record.name)
                .bind(&record.value);
        }

        query_builder.execute(&self.pool).await?;

        Ok(())
    }

    async fn get_experiment_parameter<'life2>(
        &self,
        uid: &str,
        names: &'life2 [String],
    ) -> Result<Vec<ParameterRecord>, SqlError> {
        let (query, bindings) = MySqlQueryHelper::get_experiment_parameter_query(names);
        let mut query_builder = sqlx::query_as::<_, ParameterRecord>(&query).bind(uid);

        for binding in bindings {
            query_builder = query_builder.bind(binding);
        }

        let records: Vec<ParameterRecord> = query_builder.fetch_all(&self.pool).await?;

        Ok(records)
    }
}
