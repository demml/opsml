use anyhow::Result;
use axum::{http::StatusCode, Json};
use opsml_crypt::encrypt_file;
use opsml_storage::StorageClientEnum;
use std::path::Path;
use tracing::error;

pub fn find_drift_profile(
    files: &[String],
    drift_type: &str,
) -> Result<String, (StatusCode, Json<serde_json::Value>)> {
    files
        .iter()
        .find(|f| f.as_str().contains(drift_type))
        .and_then(|f| std::path::Path::new(f.as_str()).file_name())
        .and_then(|f| f.to_str())
        .map(String::from)
        .ok_or_else(|| {
            error!("No matching drift profile found for type: {}", drift_type);
            (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "error": format!("No drift profile found for type: {}", drift_type)
                })),
            )
        })
}

pub async fn save_encrypted_profile(
    profile: &str,
    filename: &str,
    encryption_key: &[u8],
    storage_client: &StorageClientEnum,
    storage_path: &Path,
) -> Result<(), (StatusCode, Json<serde_json::Value>)> {
    let tempdir = tempfile::tempdir().map_err(|e| {
        error!("Failed to create tempdir: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to create tempdir"})),
        )
    })?;

    let temp_path = tempdir.path().join(filename);

    // Write and encrypt file
    std::fs::write(&temp_path, profile).map_err(|e| {
        error!("Failed to write profile: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to write profile"})),
        )
    })?;

    encrypt_file(&temp_path, encryption_key).map_err(|e| {
        error!("Failed to encrypt file: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to encrypt file"})),
        )
    })?;

    // Save to storage
    let new_storage_path = storage_path.join(filename);
    storage_client
        .put(&temp_path, &new_storage_path, false)
        .await
        .map_err(|e| {
            error!("Failed to save to storage: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"error": "Failed to save to storage"})),
            )
        })?;

    Ok(())
}
