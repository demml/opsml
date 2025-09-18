use crate::error::SqlError;
use opsml_settings::config::DatabaseSettings;
use sqlx::ConnectOptions;
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions, Postgres},
    Pool,
};
use tracing::debug;

#[derive(Debug, Clone)]
pub struct PostgresClient {
    pub pool: Pool<Postgres>,
}

impl PostgresClient {
    pub async fn new(settings: &DatabaseSettings) -> Result<Self, SqlError> {
        let mut opts: PgConnectOptions = settings.connection_uri.parse()?;

        opts = opts.log_statements(tracing::log::LevelFilter::Off);

        let pool = PgPoolOptions::new()
            .max_connections(settings.max_connections)
            .connect_with(opts)
            .await
            .map_err(SqlError::ConnectionError)?;

        let client = Self { pool };

        // run migrations
        client.run_migrations().await?;

        Ok(client)
    }

    async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running migrations");
        sqlx::migrate!("src/postgres/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;

        Ok(())
    }
}

pub trait BasePostgresClient {
    fn pool(&self) -> &Pool<Postgres>;
}
