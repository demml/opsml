use crate::core::error::{OpsmlServerError, internal_server_error};
use anyhow::Result;
/// Route for debugging information
use axum::{Json, http::StatusCode};
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::User;
use opsml_sql::traits::UserLogicTrait;
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
