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
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct OpsmlServerError {
    pub error: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub code: Option<&'static str>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub suggested_action: Option<&'static str>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry: Option<bool>,
}

impl OpsmlServerError {
    pub fn new(error: String) -> Self {
        OpsmlServerError {
            error,
            code: None,
            suggested_action: None,
            retry: None,
        }
    }

    pub fn not_found(resource: &str) -> Self {
        OpsmlServerError {
            error: format!("{resource} not found"),
            code: Some("NOT_FOUND"),
            suggested_action: Some("Call the corresponding list endpoint to see available resources"),
            retry: Some(false),
        }
    }

    pub fn bad_request(message: &str) -> Self {
        OpsmlServerError {
            error: message.to_string(),
            code: Some("BAD_REQUEST"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn sso_not_enabled() -> Self {
        OpsmlServerError {
            error: "SSO is not enabled".to_string(),
            code: Some("SSO_NOT_ENABLED"),
            suggested_action: Some("Configure an SSO provider or use username/password authentication"),
            retry: Some(false),
        }
    }

    pub fn permission_denied() -> Self {
        OpsmlServerError {
            error: "Permission denied".to_string(),
            code: Some("PERMISSION_DENIED"),
            suggested_action: Some("Verify your space permissions or authenticate with a different user"),
            retry: Some(false),
        }
    }

    pub fn sso_provider_not_set() -> Self {
        OpsmlServerError {
            error: "SSO provider not set".to_string(),
            code: Some("SSO_PROVIDER_NOT_SET"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn need_admin_permission() -> Self {
        error!("User does not have admin permissions");
        OpsmlServerError {
            error: "Need admin permission".to_string(),
            code: Some("PERMISSION_DENIED"),
            suggested_action: Some("This action requires admin privileges"),
            retry: Some(false),
        }
    }

    pub fn user_already_exists() -> Self {
        OpsmlServerError {
            error: "User already exists".to_string(),
            code: Some("USER_ALREADY_EXISTS"),
            suggested_action: Some("Choose a different username"),
            retry: Some(false),
        }
    }

    pub fn user_not_found() -> Self {
        OpsmlServerError {
            error: "User not found".to_string(),
            code: Some("USER_NOT_FOUND"),
            suggested_action: Some("Call GET /opsml/api/user to list users"),
            retry: Some(false),
        }
    }

    pub fn cannot_delete_last_admin() -> Self {
        error!("Cannot delete the last admin user");
        OpsmlServerError {
            error: "Cannot delete the last admin user".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: Some("Promote another user to admin before deleting this one"),
            retry: Some(false),
        }
    }

    pub fn key_header_not_found(key: String) -> Self {
        OpsmlServerError {
            error: format!("{key} header not found"),
            code: Some("VALIDATION_ERROR"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn user_validation_error() -> Self {
        error!("User validation failed");
        OpsmlServerError {
            error: "User validation failed".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn failed_token_generation() -> Self {
        error!("Failed to generate token");
        OpsmlServerError {
            error: "Failed to generate token".to_string(),
            code: Some("AUTH_TOKEN_ERROR"),
            suggested_action: None,
            retry: Some(true),
        }
    }

    pub fn refresh_token_error<T: Display>(e: T) -> Self {
        error!("Failed to refresh token: {e}");
        OpsmlServerError {
            error: "Failed to refresh token".to_string(),
            code: Some("AUTH_TOKEN_ERROR"),
            suggested_action: Some("Re-authenticate via POST /opsml/api/auth/login"),
            retry: Some(false),
        }
    }

    pub fn refresh_token_not_found() -> Self {
        error!("Refresh token not found");
        OpsmlServerError {
            error: "Refresh token not found".to_string(),
            code: Some("AUTH_MISSING_TOKEN"),
            suggested_action: Some("Re-authenticate via POST /opsml/api/auth/login"),
            retry: Some(false),
        }
    }

    pub fn jwt_decode_error<T: Display>(e: T) -> Self {
        error!("Failed to decode JWT token: {e}");
        OpsmlServerError {
            error: "Failed to decode JWT token".to_string(),
            code: Some("AUTH_INVALID_TOKEN"),
            suggested_action: Some("Re-authenticate via POST /opsml/api/auth/login"),
            retry: Some(false),
        }
    }

    pub fn no_files_found() -> Self {
        error!("No files found");
        OpsmlServerError {
            error: "No files found".to_string(),
            code: Some("NOT_FOUND"),
            suggested_action: Some("Verify the card UID and artifact path are correct"),
            retry: Some(false),
        }
    }

    pub fn file_too_large() -> Self {
        error!("File too large");
        OpsmlServerError {
            error: "File too large".to_string(),
            code: Some("FILE_TOO_LARGE"),
            suggested_action: Some("Use multipart upload for large files"),
            retry: Some(false),
        }
    }

    pub fn no_drift_profile_found() -> Self {
        error!("No drift profile found");
        OpsmlServerError {
            error: "No drift profile found".to_string(),
            code: Some("NOT_FOUND"),
            suggested_action: Some("Register a drift profile before querying drift metrics"),
            retry: Some(false),
        }
    }

    pub fn failed_to_save_to_storage<T: Display>(e: T) -> Self {
        error!("Failed to save to storage: {e}");
        OpsmlServerError {
            error: "Failed to save to storage".to_string(),
            code: Some("STORAGE_ERROR"),
            suggested_action: None,
            retry: Some(true),
        }
    }

    pub fn invalid_path() -> Self {
        error!("Invalid path");
        OpsmlServerError {
            error: "Invalid path".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn missing_session_uri() -> Self {
        error!("Missing session URI");
        OpsmlServerError {
            error: "Missing session URI".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: Some("Initiate a multipart upload before uploading parts"),
            retry: Some(false),
        }
    }

    pub fn missing_part_number() -> Self {
        error!("Missing part number");
        OpsmlServerError {
            error: "Missing part number".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn failed_to_delete_file() -> Self {
        error!("Failed to delete file");
        OpsmlServerError {
            error: "Failed to delete file".to_string(),
            code: Some("STORAGE_ERROR"),
            suggested_action: None,
            retry: Some(true),
        }
    }

    pub fn missing_space_and_name() -> Self {
        error!("Missing space and name");
        OpsmlServerError {
            error: "Missing space and name".to_string(),
            code: Some("VALIDATION_ERROR"),
            suggested_action: Some("Provide both 'space' and 'name' query parameters"),
            retry: Some(false),
        }
    }

    pub fn invalid_token() -> Self {
        error!("Invalid token");
        OpsmlServerError {
            error: "Invalid token".to_string(),
            code: Some("AUTH_INVALID_TOKEN"),
            suggested_action: Some("Re-authenticate via POST /opsml/api/auth/login"),
            retry: Some(false),
        }
    }

    pub fn missing_token() -> Self {
        error!("Missing token");
        OpsmlServerError {
            error: "Missing token".to_string(),
            code: Some("AUTH_MISSING_TOKEN"),
            suggested_action: Some("Include a Bearer token in the Authorization header"),
            retry: Some(false),
        }
    }

    pub fn invalid_recovery_code() -> Self {
        error!("Invalid recovery token");
        OpsmlServerError {
            error: "Invalid recovery token".to_string(),
            code: Some("AUTH_INVALID_TOKEN"),
            suggested_action: None,
            retry: Some(false),
        }
    }

    pub fn vec_pop_error() -> Self {
        error!("Failed to pop from vector");
        OpsmlServerError {
            error: "Failed to pop from vector".to_string(),
            code: Some("INTERNAL_ERROR"),
            suggested_action: None,
            retry: Some(true),
        }
    }

    pub fn into_response<T>(
        self,
        code: StatusCode,
    ) -> Result<T, (StatusCode, Json<OpsmlServerError>)> {
        Err((code, Json(self)))
    }
}

pub fn internal_server_error<E: std::fmt::Display>(
    _error: E,
    message: &str,
    status_code: Option<StatusCode>,
) -> (StatusCode, Json<OpsmlServerError>) {
    (
        status_code.unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),
        Json(OpsmlServerError {
            error: message.to_string(),
            code: Some("INTERNAL_ERROR"),
            suggested_action: None,
            retry: Some(true),
        }),
    )
}

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

impl ServerError {
    pub fn is_unique_violation(&self) -> bool {
        match self {
            ServerError::SqlError(sql_err) => sql_err.is_unique_violation(),
            _ => false,
        }
    }
}
