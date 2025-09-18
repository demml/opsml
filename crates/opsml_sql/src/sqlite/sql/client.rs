use crate::{
    error::SqlError,
    sqlite::sql::{card::CardLogicSqliteClient, experiment::ExperimentLogicSqliteClient},
};
use opsml_settings::config::DatabaseSettings;
use sqlx::{sqlite::SqlitePoolOptions, Pool, Sqlite};
use std::path::Path;
use tracing::{debug, instrument};

#[derive(Debug)]
pub struct SqliteClient {
    pub pool: Pool<Sqlite>,
    pub card: CardLogicSqliteClient,
    pub exp: ExperimentLogicSqliteClient,
}

impl SqliteClient {
    pub async fn new(settings: &DatabaseSettings) -> Result<SqliteClient, SqlError> {
        // Create SQLite file if it doesn't exist and not in-memory
        if !settings.connection_uri.contains(":memory:") {
            let uri = settings.connection_uri.replace("sqlite://", "");
            let path = Path::new(&uri);

            if !path.exists() {
                debug!("SQLite file does not exist, creating file at: {}", uri);

                // Ensure parent directory exists
                if let Some(parent) = path.parent() {
                    if !parent.exists() {
                        std::fs::create_dir_all(parent)
                            .map_err(|e| SqlError::ConnectionError(sqlx::Error::Io(e)))?;
                    }
                }

                // Create the file
                std::fs::File::create(&uri)
                    .map_err(|e| SqlError::ConnectionError(sqlx::Error::Io(e)))?;
            }
        }

        let pool = SqlitePoolOptions::new()
            .max_connections(settings.max_connections)
            .connect(&settings.connection_uri)
            .await
            .map_err(SqlError::ConnectionError)?;

        let client = SqliteClient {
            card: CardLogicSqliteClient::new(&pool),
            exp: ExperimentLogicSqliteClient::new(&pool),
            pool,
        };

        // Run migrations
        client.run_migrations().await?;

        debug!("SQLite client initialized successfully");
        Ok(client)
    }

    #[instrument(skip(self))]
    async fn run_migrations(&self) -> Result<(), SqlError> {
        debug!("Running SQLite migrations");
        sqlx::migrate!("src/sqlite/migrations")
            .run(&self.pool)
            .await
            .map_err(SqlError::MigrationError)?;
        debug!("SQLite migrations completed successfully");
        Ok(())
    }
}

pub trait BaseSqliteClient {
    fn pool(&self) -> &Pool<Sqlite>;
}
