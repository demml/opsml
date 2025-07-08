use crate::core::error::ServerError;
use anyhow::Result;
use opsml_crypt::{
    decrypt_directory, decrypt_file, encrypt_directory,
    key::{derive_encryption_key, encrypted_key, generate_salt},
};
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;

use opsml_storage::StorageClientEnum;
use opsml_types::contracts::{ArtifactKey, DownloadResponse, UploadResponse};
use opsml_types::RegistryType;
use opsml_utils::uid_to_byte_key;

use std::path::{Path, PathBuf};
/// Route for debugging information
use std::sync::Arc;
use tempfile::TempDir;
use tracing::debug;
use tracing::{error, instrument};
use uuid::Uuid;

#[instrument(skip_all)]
pub async fn create_artifact_key(
    sql_client: &SqlClientEnum,
    encryption_key: &[u8],
    uid: &str,
    space: &str,
    registry_type: &str,
    storage_key: &str,
) -> Result<ArtifactKey, ServerError> {
    debug!(
        "Creating artifact key for: {:?} and path {:?}",
        uid, storage_key
    );
    let salt = generate_salt()?;

    // create derived key
    let derived_key = derive_encryption_key(encryption_key, &salt, registry_type.as_bytes())?;
    let uid_key = uid_to_byte_key(uid)?;

    // encrypt key before sending
    let encrypted_key = encrypted_key(&uid_key, &derived_key)?;

    // spawn a task to insert the key into the database

    let artifact_key = ArtifactKey {
        uid: uid.to_string(),
        space: space.to_string(),
        registry_type: RegistryType::from_string(registry_type)?,
        encrypted_key,
        storage_key: storage_key.to_string(),
    };

    // Spawn task and add to managed set
    sql_client
        .insert_artifact_key(&artifact_key)
        .await
        .inspect_err(|e| {
            error!("Failed to insert artifact key: {e}");
        })?;

    Ok(artifact_key)
}

pub async fn create_and_store_encrypted_file(
    storage_client: Arc<StorageClientEnum>,
    content: &str,
    lpath: &str,
    rpath: &str,
    key: &ArtifactKey,
) -> Result<UploadResponse, ServerError> {
    let encryption_key = key.get_decrypt_key().inspect_err(|e| {
        error!("Failed to get decryption key: {e}");
    })?;

    // Create temp directory
    let tmp_dir = TempDir::new().inspect_err(|e| {
        error!("Failed to create temp dir: {e}");
    })?;

    // Create local path
    let local_path = tmp_dir.path().join(lpath);

    // Write content to file
    std::fs::write(&local_path, content).inspect_err(|e| {
        error!("Failed to write content to file: {e}");
    })?;

    // Encrypt directory
    encrypt_directory(&local_path, &encryption_key).inspect_err(|e| {
        error!("Failed to encrypt directory: {e}");
    })?;

    let remote_path = PathBuf::from(rpath);
    // Store file
    storage_client
        .put(&local_path, &remote_path, false)
        .await
        .inspect_err(|e| {
            error!("Failed to store file: {e}");
        })?;

    Ok(UploadResponse {
        uploaded: true,
        message: "File uploaded successfully".to_string(),
    })
}

#[instrument(skip_all)]
pub async fn download_artifact(
    storage_client: Arc<StorageClientEnum>,
    sql_client: Arc<SqlClientEnum>,
    lpath: &Path,
    rpath: &str,
    registry_type: &str,
    uid: Option<&str>,
) -> Result<DownloadResponse, ServerError> {
    let key = if uid.is_none() {
        sql_client
            .get_artifact_key_from_path(rpath, registry_type)
            .await
            .inspect_err(|e| {
                error!("Failed to get artifact key: {e}");
            })?
    } else {
        Some(
            sql_client
                .get_artifact_key(uid.unwrap(), registry_type)
                .await
                .inspect_err(|e| {
                    error!("Failed to get artifact key: {e}");
                })?,
        )
    };

    if key.is_none() {
        return Err(ServerError::ArtifactKeyNotFound);
    }

    let key = key.unwrap();
    let rpath = PathBuf::from(rpath);

    // Check if file exists in storage
    let files = storage_client.find(&rpath).await.inspect_err(|e| {
        error!("Failed to find artifact: {e}");
    })?;

    if files.is_empty() {
        return Err(ServerError::ArtifactNotFound);
    }

    // Set up paths
    let remote_file = PathBuf::from(&files[0]);

    // Download file
    storage_client
        .get(lpath, &remote_file, false)
        .await
        .inspect_err(|e| {
            error!("Failed to download artifact: {e}");
        })?;

    // Get decryption key and decrypt
    let decryption_key = key.get_decrypt_key().inspect_err(|e| {
        error!("Failed to get decryption key: {e}");
    })?;

    decrypt_file(lpath, &decryption_key).inspect_err(|e| {
        error!("Failed to decrypt artifact: {e}");
    })?;

    Ok(DownloadResponse { exists: true })
}

#[instrument(skip_all)]
pub async fn download_artifacts(
    storage_client: Arc<StorageClientEnum>,
    sql_client: Arc<SqlClientEnum>,
    lpath: &Path,
    rpath: &Path,
    registry_type: &str,
    uid: Option<&str>,
) -> Result<DownloadResponse, ServerError> {
    let key = sql_client
        .get_artifact_key(uid.unwrap(), registry_type)
        .await
        .inspect_err(|e| {
            error!("Failed to get artifact key: {e}");
        })?;

    let rpath = key.storage_path().join(rpath);

    // Check if file exists in storage
    let files = storage_client.find(&rpath).await.inspect_err(|e| {
        error!("Failed to find artifact: {e}");
    })?;

    if files.is_empty() {
        return Err(ServerError::ArtifactNotFound);
    }

    // Download files
    storage_client
        .get(lpath, &rpath, true)
        .await
        .inspect_err(|e| {
            error!("Failed to download artifact: {e}");
        })?;

    // Get decryption key and decrypt
    let decryption_key = key.get_decrypt_key().inspect_err(|e| {
        error!("Failed to get decryption key: {e}");
    })?;

    decrypt_directory(lpath, &decryption_key).inspect_err(|e| {
        error!("Failed to decrypt artifact: {e}");
    })?;

    Ok(DownloadResponse { exists: true })
}

pub async fn get_artifact_key(
    sql_client: &SqlClientEnum,
    encryption_key: &[u8],
    registry_type: &str,
    space: &str,
    storage_key: &str,
) -> Result<ArtifactKey, ServerError> {
    match sql_client
        .get_artifact_key_from_path(storage_key, registry_type)
        .await
        .inspect_err(|e| {
            error!("Failed to get artifact key: {e}");
        })? {
        Some(key) => Ok(key),
        None => {
            let uid = Uuid::new_v4().to_string();
            create_artifact_key(
                sql_client,
                encryption_key,
                &uid,
                space,
                registry_type,
                storage_key,
            )
            .await
        }
    }
}
