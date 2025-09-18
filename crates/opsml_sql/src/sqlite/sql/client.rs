use crate::base::SqlClient;

use crate::error::SqlError;
use crate::schemas::schema::{
    ArtifactSqlRecord, AuditCardRecord, CardResults, CardSummary, DataCardRecord,
    ExperimentCardRecord, HardwareMetricsRecord, MetricRecord, ModelCardRecord, ParameterRecord,
    PromptCardRecord, QueryStats, ServerCard, ServiceCardRecord, SqlSpaceRecord, User,
    VersionResult, VersionSummary,
};

use crate::sqlite::helper::SqliteQueryHelper;
use async_trait::async_trait;
use opsml_semver::VersionValidator;
use opsml_settings::config::DatabaseSettings;
use opsml_types::contracts::{
    ArtifactKey, ArtifactQueryArgs, ArtifactRecord, AuditEvent, SpaceNameEvent, SpaceRecord,
    SpaceStats,
};
use opsml_types::{cards::CardTable, contracts::CardQueryArgs, RegistryType};
use semver::Version;
use sqlx::{
    sqlite::{SqlitePoolOptions, SqliteRow},
    FromRow, Pool, Row, Sqlite,
};
use std::path::Path;
use tracing::{debug, error, instrument};

#[derive(Debug, Clone)]
pub struct SqliteClient {
    pub pool: Pool<Sqlite>,
}

impl SqliteClient {
    async fn new(settings: &DatabaseSettings) -> Result<SqliteClient, SqlError> {
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

        let client = SqliteClient { pool };

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
