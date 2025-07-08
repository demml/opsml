use crate::core::error::{internal_server_error, OpsmlServerError};
use anyhow::Result;
/// Route for debugging information
use axum::{http::StatusCode, Json};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::User;
use tracing::error;

/// Resuable function to get a user from the database
///
/// # Parameters
///
/// - `state` - The application state
/// - `username` - The username of the user to get
///
/// # Returns
///
/// Returns a `Result` containing either the user or an error
///
/// # Errors
/// Returns an error if the user is not found in the database
///
/// # Panics
///
/// Panics if the user cannot be retrieved from the database
pub async fn get_user(
    sql_client: &SqlClientEnum,
    username: &str,
    auth_type: Option<&str>,
) -> Result<User, (StatusCode, Json<OpsmlServerError>)> {
    sql_client
        .get_user(username, auth_type)
        .await
        .map_err(|e| {
            error!("Failed to get user from database: {e}");
            internal_server_error(e, "Failed to get user from database")
        })?
        .ok_or_else(|| {
            error!("User not found in database");
            (
                StatusCode::NOT_FOUND,
                Json(OpsmlServerError::user_not_found()),
            )
        })
}
