use anyhow::Result;
use opsml_crypt::key::{derive_encryption_key, encrypted_key, generate_salt};
use opsml_error::ApiError;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;

use opsml_types::contracts::ArtifactKey;
use opsml_types::RegistryType;
use opsml_utils::uid_to_byte_key;

/// Route for debugging information
use std::sync::Arc;
use tracing::debug;
use tracing::{error, instrument};

#[instrument(skip_all)]
pub async fn create_artifact_key(
    sql_client: Arc<SqlClientEnum>,
    encryption_key: Vec<u8>,
    uid: &str,
    registry_type: &str,
    storage_key: &str,
) -> Result<ArtifactKey, ApiError> {
    debug!("Creating artifact key for: {:?}", uid);
    let salt = generate_salt();

    // create derived key
    let derived_key = derive_encryption_key(&encryption_key, &salt, registry_type.as_bytes())?;

    debug!("Derived key: {:?}", derived_key);
    let uid_key = uid_to_byte_key(uid)?;

    // encrypt key before sending
    let encrypted_key = encrypted_key(&uid_key, &derived_key)?;
    debug!("Encrypted key: {:?}", encrypted_key);

    // spawn a task to insert the key into the database

    let artifact_key = ArtifactKey {
        uid: uid.to_string(),
        registry_type: RegistryType::from_string(registry_type)?,
        encrypted_key,
        storage_key: storage_key.to_string(),
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
