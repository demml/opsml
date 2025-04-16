use std::fmt::Display;

use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};
use tracing::error;

/// Error structure for OpsML server
/// This structure is used to return error messages in a consistent format
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct OpsmlServerError {
    pub error: String,
}

impl OpsmlServerError {
    pub fn permission_denied() -> Self {
        OpsmlServerError {
            error: "Permission denied".to_string(),
        }
    }

    pub fn need_admin_permission() -> Self {
        error!("User does not have admin permissions");
        OpsmlServerError {
            error: "Need admin permission".to_string(),
        }
    }

    pub fn user_already_exists() -> Self {
        OpsmlServerError {
            error: "User already exists".to_string(),
        }
    }

    pub fn user_not_found() -> Self {
        OpsmlServerError {
            error: "User not found".to_string(),
        }
    }

    pub fn cannot_delete_last_admin() -> Self {
        error!("Cannot delete the last admin user");
        OpsmlServerError {
            error: "Cannot delete the last admin user".to_string(),
        }
    }
    pub fn username_header_not_found() -> Self {
        error!("Username header not found");
        OpsmlServerError {
            error: "Username header not found".to_string(),
        }
    }

    pub fn invalid_username_format() -> Self {
        error!("Invalid username format");
        OpsmlServerError {
            error: "Invalid username format".to_string(),
        }
    }

    pub fn password_header_not_found() -> Self {
        error!("Password header not found");
        OpsmlServerError {
            error: "Password header not found".to_string(),
        }
    }
    pub fn invalid_password_format() -> Self {
        error!("Invalid password format");
        OpsmlServerError {
            error: "Invalid password format".to_string(),
        }
    }

    pub fn user_validation_error() -> Self {
        error!("User validation failed");
        OpsmlServerError {
            error: "User validation failed".to_string(),
        }
    }

    pub fn failed_token_generation() -> Self {
        error!("Failed to generate token");
        OpsmlServerError {
            error: "Failed to generate token".to_string(),
        }
    }

    pub fn bearer_token_not_found() -> Self {
        error!("Bearer token not found");
        OpsmlServerError {
            error: "Bearer token not found".to_string(),
        }
    }

    pub fn refresh_token_error<T: Display>(e: T) -> Self {
        error!("Failed to refresh token: {}", e);
        OpsmlServerError {
            error: "Failed to refresh token".to_string(),
        }
    }

    pub fn refresh_token_not_found() -> Self {
        error!("Refresh token not found");
        OpsmlServerError {
            error: "Refresh token not found".to_string(),
        }
    }

    pub fn jwt_decode_error<T: Display>(e: T) -> Self {
        error!("Failed to decode JWT token: {}", e);
        OpsmlServerError {
            error: "Failed to decode JWT token".to_string(),
        }
    }

    pub fn new(error: String) -> Self {
        OpsmlServerError { error }
    }

    pub fn no_files_found() -> Self {
        error!("No files found");
        OpsmlServerError {
            error: "No files found".to_string(),
        }
    }

    pub fn file_too_large() -> Self {
        error!("File too large");
        OpsmlServerError {
            error: "File too large".to_string(),
        }
    }

    pub fn no_drift_profile_found() -> Self {
        error!("No drift profile found");
        OpsmlServerError {
            error: "No drift profile found".to_string(),
        }
    }

    pub fn failed_to_save_to_storage<T: Display>(e: T) -> Self {
        error!("Failed to save to storage: {}", e);
        OpsmlServerError {
            error: "Failed to save to storage".to_string(),
        }
    }

    pub fn invalid_path() -> Self {
        error!("Invalid path");
        OpsmlServerError {
            error: "Invalid path".to_string(),
        }
    }

    pub fn missing_session_uri() -> Self {
        error!("Missing session URI");
        OpsmlServerError {
            error: "Missing session URI".to_string(),
        }
    }

    pub fn missing_part_number() -> Self {
        error!("Missing part number");
        OpsmlServerError {
            error: "Missing part number".to_string(),
        }
    }

    pub fn failed_to_delete_file() -> Self {
        error!("Failed to delete file");
        OpsmlServerError {
            error: "Failed to delete file".to_string(),
        }
    }

    pub fn missing_space_and_name() -> Self {
        error!("Missing space and name");
        OpsmlServerError {
            error: "Missing space and name".to_string(),
        }
    }

    pub fn invalid_token() -> Self {
        error!("Invalid token");
        OpsmlServerError {
            error: "Invalid token".to_string(),
        }
    }

    pub fn to_error<T>(self, code: StatusCode) -> Result<T, (StatusCode, Json<OpsmlServerError>)> {
        Err((code, Json(self)))
    }
}

/// Generic function for returning server errors
pub fn internal_server_error<E: std::fmt::Display>(
    error: E,
    message: &str,
) -> (StatusCode, Json<OpsmlServerError>) {
    let msg = format!("{}: {}", message, error);
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(OpsmlServerError::new(msg)),
    )
}
