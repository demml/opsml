use crate::core::error::internal_server_error;
use crate::core::state::AppState;
use axum::extract::DefaultBodyLimit;
use axum::extract::Multipart;
use axum::{
    body::Body,
    extract::{Query, State},
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::{delete, get, post},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_error::ApiError;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_sql::schemas::ArtifactKey;
use opsml_types::{contracts::*, StorageType, MAX_FILE_SIZE};
use opsml_utils::uid_to_byte_key;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;

use anyhow::{Context, Result};
use opsml_crypt::key::{derive_encryption_key, encrypt_key, generate_salt};
use opsml_error::error::ServerError;

/// Route for debugging information
use std::sync::Arc;
use tracing::debug;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn create_artifact_key(
    sql_client: Arc<SqlClientEnum>,
    encryption_key: Vec<u8>,
    uid: &str,
    card_type: &str,
) -> Result<ArtifactKey, ApiError> {
    debug!("Creating artifact key for: {:?}", uid);
    let salt = generate_salt();

    // create derived key
    let derived_key = derive_encryption_key(&encryption_key, &salt, card_type.as_bytes())?;

    debug!("Derived key: {:?}", derived_key);
    let uid_key = uid_to_byte_key(uid)?;

    // encrypt key before sending
    let encrypted_key = encrypt_key(&uid_key, &derived_key)?;
    debug!("Encrypted key: {:?}", encrypted_key);

    // spawn a task to insert the key into the database

    let artifact_key = ArtifactKey {
        uid: uid.to_string(),
        card_type: card_type.to_string(),
        encrypt_key: encrypted_key,
    };

    // clone the artifact_key before moving it into the async block
    let artifact_key_clone = artifact_key.clone();
    // Spawn task and add to managed set
    tokio::spawn(async move {
        if let Err(e) = sql_client.insert_artifact_key(&artifact_key_clone).await {
            error!("Failed to insert artifact key: {}", e);
        }
    });

    Ok(artifact_key)
}
