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

impl SqlError {
    /// Returns true if this error is a row-not-found from sqlx.
    pub fn is_row_not_found(&self) -> bool {
        matches!(self, SqlError::SqlxError(sqlx::Error::RowNotFound))
    }

    /// Returns true if this error is a unique constraint violation.
    pub fn is_unique_violation(&self) -> bool {
        let sqlx_err = match self {
            SqlError::SqlxError(e) => e,
            _ => return false,
        };

        if let sqlx::Error::Database(db_err) = sqlx_err {
            // Postgres: 23505, MySQL: 1062, SQLite: 2067 (SQLITE_CONSTRAINT_UNIQUE)
            if let Some(code) = db_err.code()
                && (code == "23505" || code == "1062" || code == "2067")
            {
                return true;
            }
            // Fallback: SQLite may also report via message string
            if db_err.message().contains("UNIQUE constraint failed") {
                return true;
            }
        }

        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn non_sqlx_error_variants_return_false() {
        assert!(!SqlError::InvalidTableName.is_unique_violation());
        assert!(!SqlError::InvalidCardType.is_unique_violation());
        assert!(!SqlError::MissingField("x".into()).is_unique_violation());
    }

    #[test]
    fn sqlx_row_not_found_returns_false() {
        let err = SqlError::SqlxError(sqlx::Error::RowNotFound);
        assert!(!err.is_unique_violation());
    }

    #[test]
    fn sqlx_column_not_found_returns_false() {
        let err = SqlError::SqlxError(sqlx::Error::ColumnNotFound("col".into()));
        assert!(!err.is_unique_violation());
    }
}
