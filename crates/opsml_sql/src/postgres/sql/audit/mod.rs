use crate::{postgres::helper::PostgresQueryHelper, traits::AuditLogicTrait};

use crate::error::SqlError;
use async_trait::async_trait;
use opsml_types::contracts::AuditEvent;
use sqlx::{Pool, Postgres};

#[derive(Debug, Clone)]
pub struct AuditLogicPostgresClient {
    pool: sqlx::Pool<Postgres>,
}
impl AuditLogicPostgresClient {
    pub fn new(pool: &Pool<Postgres>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl AuditLogicTrait for AuditLogicPostgresClient {
    async fn insert_audit_event(&self, event: AuditEvent) -> Result<(), SqlError> {
        let query = PostgresQueryHelper::get_audit_event_insert_query();
        sqlx::query(&query)
            .bind(event.username)
            .bind(event.client_ip)
            .bind(event.user_agent)
            .bind(event.operation.to_string())
            .bind(event.resource_type.to_string())
            .bind(event.resource_id)
            .bind(event.access_location)
            .bind(event.status.to_string())
            .bind(event.error_message)
            .bind(event.metadata)
            .bind(event.registry_type.map(|r| r.to_string()))
            .bind(event.route)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
