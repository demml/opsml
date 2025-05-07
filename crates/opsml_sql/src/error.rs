use opsml_types::error::TypeError;
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
}
