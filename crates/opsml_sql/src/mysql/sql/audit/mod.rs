use crate::{mysql::helper::MySqlQueryHelper, traits::AuditLogicTrait};

use crate::error::SqlError;
use async_trait::async_trait;
use opsml_types::contracts::AuditEvent;
use sqlx::{MySql, Pool};

#[derive(Debug, Clone)]
pub struct AuditLogicMySqlClient {
    pool: sqlx::Pool<MySql>,
}
impl AuditLogicMySqlClient {
    pub fn new(pool: &Pool<MySql>) -> Self {
        Self { pool: pool.clone() }
    }
}

#[async_trait]
impl AuditLogicTrait for AuditLogicMySqlClient {
    async fn insert_audit_event(&self, event: AuditEvent) -> Result<(), SqlError> {
        let query = MySQLQueryHelper::get_audit_event_insert_query();
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
