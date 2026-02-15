use axum::Json;
use axum::http::StatusCode;
use opsml_auth::error::AuthError;
use opsml_crypt::error::CryptError;
use opsml_semver::error::VersionError;
use opsml_sql::error::SqlError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::TypeError;
use opsml_utils::error::UtilError;
use serde::{Deserialize, Serialize};
use std::fmt::Display;
use thiserror::Error;
use tracing::error;

/// Error structure for OpsML server
/// This structure is used to return error messages in a consistent format
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct OpsmlServerError {
    pub error: String,
}

impl OpsmlServerError {
    pub fn sso_not_enabled() -> Self {
        OpsmlServerError {
            error: "SSO is not enabled".to_string(),
        }
    }
    pub fn permission_denied() -> Self {
        OpsmlServerError {
            error: "Permission denied".to_string(),
        }
    }

    pub fn sso_provider_not_set() -> Self {
        OpsmlServerError {
            error: "SSO provider not set".to_string(),
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
    pub fn key_header_not_found(key: String) -> Self {
        OpsmlServerError {
            error: format!("{key} header not found"),
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

    pub fn refresh_token_error<T: Display>(e: T) -> Self {
        error!("Failed to refresh token: {e}");
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
        error!("Failed to decode JWT token: {e}");
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
        error!("Failed to save to storage: {e}");
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

    pub fn missing_token() -> Self {
        error!("Missing token");
        OpsmlServerError {
            error: "Missing token".to_string(),
        }
    }

    pub fn invalid_recovery_code() -> Self {
        error!("Invalid recovery token");
        OpsmlServerError {
            error: "Invalid recovery token".to_string(),
        }
    }

    pub fn vec_pop_error() -> Self {
        error!("Failed to pop from vector");
        OpsmlServerError {
            error: "Failed to pop from vector".to_string(),
        }
    }

    pub fn into_response<T>(
        self,
        code: StatusCode,
    ) -> Result<T, (StatusCode, Json<OpsmlServerError>)> {
        Err((code, Json(self)))
    }
}

/// Generic function for returning server errors
pub fn internal_server_error<E: std::fmt::Display>(
    error: E,
    message: &str,
) -> (StatusCode, Json<OpsmlServerError>) {
    let msg = format!("{message}: {error}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(OpsmlServerError::new(msg)),
    )
}

// Server error enum
// reminder: none of this Errors should implement a pyerr conversion
// pyerr will require a python runtime. In rust-only code (like the server) we
// don't want this
#[derive(Error, Debug)]
pub enum ServerError {
    #[error("Failed to create client with error: {0}")]
    CreateClientError(#[source] reqwest::Error),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    AuthError(#[from] AuthError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Failed to load drift profile from string: {0}")]
    LoadDriftProfileError(String),

    #[error(transparent)]
    SqlError(#[from] SqlError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error("Artifact key not found")]
    ArtifactKeyNotFound,

    #[error("Artifact not found")]
    ArtifactNotFound,

    #[error(transparent)]
    VersionError(#[from] VersionError),

    #[error("User not found in database")]
    UserNotFoundError,

    #[error(transparent)]
    StripPrefixError(#[from] std::path::StripPrefixError),

    #[error("File too large: {0}")]
    FileTooLargeError(String),

    #[error(transparent)]
    JoinError(#[from] tokio::task::JoinError),
}
