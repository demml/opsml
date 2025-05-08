use opsml_sql::error::SqlError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum EventError {
    #[error("Failed to log event")]
    LogEventError(#[source] SqlError),
}
