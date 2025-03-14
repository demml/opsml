use anyhow::Result;
use opsml_crypt::{
    decrypt_directory, encrypt_directory,
    key::{derive_encryption_key, encrypted_key, generate_salt},
};
use opsml_error::ApiError;
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
    sql_client: Arc<SqlClientEnum>,
    encryption_key: Vec<u8>,
    uid: &str,
    registry_type: &str,
    storage_key: &str,
) -> Result<ArtifactKey, ApiError> {
    debug!("Creating artifact key for: {:?}", uid);
    let salt = generate_salt()?;

    // create derived key
    let derived_key = derive_encryption_key(&encryption_key, &salt, registry_type.as_bytes())?;
    let uid_key = uid_to_byte_key(uid)?;

    // encrypt key before sending
    let encrypted_key = encrypted_key(&uid_key, &derived_key)?;

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

pub async fn create_and_store_encrypted_file(
    storage_client: Arc<StorageClientEnum>,
    content: &str,
    lpath: &str,
    rpath: &str,
    key: ArtifactKey,
) -> Result<UploadResponse, ApiError> {
    let encryption_key = key.get_decrypt_key().map_err(|e| {
        error!("Failed to get decryption key: {}", e);
        ApiError::Error("Failed to get decryption key".to_string())
    })?;

    // Create temp directory
    let tmp_dir = TempDir::new().map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        ApiError::Error("Failed to create temp dir".to_string())
    })?;

    // Create local path
    let local_path = tmp_dir.path().join(lpath);

    // Write content to file
    std::fs::write(&local_path, content).map_err(|e| {
        error!("Failed to write content to file: {}", e);
        ApiError::Error("Failed to write content to file".to_string())
    })?;

    // Encrypt directory
    encrypt_directory(&local_path, &encryption_key).map_err(|e| {
        error!("Failed to encrypt directory: {}", e);
        ApiError::Error("Failed to encrypt directory".to_string())
    })?;

    let remote_path = PathBuf::from(rpath);
    // Store file
    storage_client
        .put(&local_path, &remote_path, false)
        .await
        .map_err(|e| {
            error!("Failed to store file: {}", e);
            ApiError::Error("Failed to store file".to_string())
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
) -> Result<DownloadResponse, ApiError> {
    let key = sql_client
        .get_artifact_key_from_path(rpath, registry_type)
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            ApiError::Error("Failed to get artifact key".to_string())
        })?;

    if key.is_none() {
        return Err(ApiError::Error("Artifact key not found".to_string()));
    }

    let key = key.unwrap();
    let rpath = PathBuf::from(rpath);

    // Check if file exists in storage
    let files = storage_client.find(&rpath).await.map_err(|e| {
        error!("Failed to find artifact: {}", e);
        ApiError::Error("Failed to find artifact".to_string())
    })?;

    if files.is_empty() {
        return Err(ApiError::Error("Artifact not found".to_string()));
    }

    // Set up paths
    let remote_file = PathBuf::from(&files[0]);

    // Download file
    storage_client
        .get(lpath, &remote_file, false)
        .await
        .map_err(|e| {
            error!("Failed to download artifact: {}", e);
            ApiError::Error("Failed to download artifact".to_string())
        })?;

    // Get decryption key and decrypt
    let decryption_key = key.get_decrypt_key().map_err(|e| {
        error!("Failed to get decryption key: {}", e);
        ApiError::Error("Failed to get decryption key".to_string())
    })?;

    decrypt_directory(lpath, &decryption_key).map_err(|e| {
        error!("Failed to decrypt artifact: {}", e);
        ApiError::Error("Failed to decrypt artifact".to_string())
    })?;

    Ok(DownloadResponse { exists: true })
}

pub async fn get_artifact_key(
    sql_client: Arc<SqlClientEnum>,
    encryption_key: Vec<u8>,
    registry_type: &str,
    storage_key: &str,
) -> Result<ArtifactKey, ApiError> {
    match sql_client
        .get_artifact_key_from_path(storage_key, registry_type)
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            ApiError::Error("Failed to get artifact key".to_string())
        })? {
        Some(key) => Ok(key),
        None => {
            let uid = Uuid::new_v4().to_string();
            create_artifact_key(
                sql_client.clone(),
                encryption_key,
                &uid,
                registry_type,
                storage_key,
            )
            .await
        }
    }
}
