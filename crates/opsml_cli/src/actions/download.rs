use crate::cli::arg::DownloadCard;
use crate::cli::arg::IntoQueryArgs;
use opsml_crypt::decrypt_directory;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
use opsml_storage::storage_client;
use opsml_types::contracts::ArtifactKey;
use owo_colors::OwoColorize;
use std::path::PathBuf;

/// Download all artifacts of a card
///
/// # Arguments
///
/// * `key` - ArtifactKey
/// * `write_dir` - str
///
/// # Returns
///
/// Result<(), CliError>
fn download_card_artifacts(key: &ArtifactKey, write_dir: &str) -> Result<(), CliError> {
    // get registry
    let decryption_key = key.get_decrypt_key()?;
    let rpath = key.storage_path();

    // create write dir if not exists
    let lpath = PathBuf::from(write_dir);
    if !lpath.exists() {
        std::fs::create_dir_all(&lpath).map_err(|e| CliError::Error(format!("{}", e)))?;
    }
    // download card artifacts
    storage_client()
        .map_err(|e| CliError::Error(format!("{}", e)))?
        .get(&lpath, &rpath, true)
        .map_err(|e| CliError::Error(format!("{}", e)))?;

    decrypt_directory(&lpath, &decryption_key)?;

    Ok(())
}

pub fn download_card(args: &DownloadCard) -> Result<(), CliError> {
    // convert to query args
    let query_args = args.into_query_args()?;

    // get registry
    let registry = OpsmlRegistry::new(query_args.registry_type.clone())?;

    let key = registry.load_card(query_args)?;

    println!(
        "Downloading card artifacts from registry: {} for path: {}",
        args.registry,
        key.storage_key.to_string().green()
    );

    download_card_artifacts(&key, &args.write_dir)?;

    Ok(())
}
