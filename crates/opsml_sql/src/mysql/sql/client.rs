use crate::error::SqlError;
use opsml_settings::config::DatabaseSettings;
use sqlx::{
    mysql::{MySql, MySqlPoolOptions},
    Pool,
};
use tracing::debug;

#[derive(Debug, Clone)]
pub struct MySqlClient {
    pub pool: Pool<MySql>,
}

impl MySqlClient {
    pub async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        let pool = MySqlPoolOptions::new()
            .max_connections(settings.max_connections)
            .connect(&settings.connection_uri)
            .await
            .map_err(SqlError::ConnectionError)?;

        let client = Self { pool };

        // run migrations
        client.run_migrations().await?;

        Ok(client)
    }
    async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running migrations");
        sqlx::migrate!("src/mysql/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;

        Ok(())
    }
}

pub trait BaseMySqlClient {
    fn pool(&self) -> &Pool<MySql>;
}
