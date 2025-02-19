use anyhow::Result;
use opsml_crypt::key::{derive_encryption_key, encrypted_key, generate_salt};
use opsml_error::ApiError;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_storage::StorageClientEnum;
use opsml_types::cards::CardTable;
use opsml_types::contracts::{ArtifactKey, CardQueryArgs};
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

#[instrument(skip_all)]
pub async fn cleanup_artifacts(
    storage_client: &Arc<StorageClientEnum>,
    sql_client: &Arc<SqlClientEnum>,
    uid: String,
    registry_type: RegistryType,
    table: &CardTable,
) -> Result<(), ApiError> {
    // get artifact key
    let key = sql_client
        .get_card_key_for_loading(
            table,
            &CardQueryArgs {
                uid: Some(uid.clone()),
                registry_type: registry_type.clone(),
                ..Default::default()
            },
        )
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            ApiError::Error("Failed to get artifact key".to_string())
        })?;

    storage_client
        .rm(&key.storage_path(), true)
        .await
        .map_err(|e| {
            error!("Failed to remove artifact: {}", e);
            ApiError::Error("Failed to remove artifact".to_string())
        })?;

    sql_client
        .delete_artifact_key(&uid, &registry_type.to_string())
        .await
        .map_err(|e| {
            error!("Failed to delete artifact key: {}", e);
            ApiError::Error("Failed to delete artifact key".to_string())
        })?;

    Ok(())
}
