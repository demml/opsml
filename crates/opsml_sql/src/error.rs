use opsml_semver::error::VersionError;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SqlError {
    #[error(transparent)]
    SqlxError(#[from] sqlx::Error),

    #[error("Failed to connect to database")]
    ConnectionError(#[source] sqlx::Error),

    #[error("Migration error")]
    MigrationError(#[source] sqlx::migrate::MigrateError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    SemverError(#[from] VersionError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Invalid table name")]
    InvalidTableName,

    #[error("Invalid card type")]
    InvalidCardType,

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error("Service type is not MCP: {0}")]
    InvalidServiceType(String),

    #[error("Missing required field: {0}")]
    MissingField(String),
}
