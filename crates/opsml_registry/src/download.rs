use crate::async_base::AsyncOpsmlRegistry;
use crate::base::OpsmlRegistry;
use crate::error::RegistryError;
use opsml_cards::Card;
use opsml_cards::ModelCard;
use opsml_cards::PromptCard;
use opsml_cards::ServiceCard;
use opsml_colors::Colorize;
use opsml_crypt::decrypt_directory;
use opsml_storage::{async_storage_client, storage_client};
use opsml_types::{
    cards::ServiceCardMapping,
    contracts::{ArtifactKey, CardQueryArgs},
    RegistryType, SaveName, Suffix,
};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use std::path::Path;
use std::path::PathBuf;
use tracing::{debug, instrument};
/// Download all artifacts of a card
///
/// # Arguments
/// * `key` - ArtifactKey
/// * `write_dir` - str
///
/// # Returns
///
/// Result<(), CliError>
fn download_card_artifacts(key: &ArtifactKey, lpath: &Path) -> Result<(), RegistryError> {
    // get registry
    let decryption_key = key.get_decrypt_key()?;
    let rpath = key.storage_path();

    if !lpath.exists() {
        std::fs::create_dir_all(lpath)?;
    }
    // download card artifacts
    storage_client()?.get(lpath, &rpath, true)?;

    decrypt_directory(lpath, &decryption_key)?;

    Ok(())
}

/// Download all artifacts of a card
///
/// # Arguments
/// * `args` - DownloadCard
/// * `registry_type` - RegistryType
///
/// # Returns
/// None
///
/// # Errors
/// RegistryError
pub fn download_card_from_registry(
    args: &CardQueryArgs,
    write_path: PathBuf,
) -> Result<(), RegistryError> {
    // get registry
    let registry = OpsmlRegistry::new(args.registry_type.clone())?;

    // Steps:
    // 1. Load the ServiceCard from the registry
    // 2. Get all cards in the service
    // 3. For each card, get the ArtifactKey, download the artifacts, and decrypt them
    // 4. Save the artifacts to the specified directory

    let key = registry.get_key(args)?;

    let names: Vec<&str> = key
        .storage_key
        .split('/')
        .skip(1) // Skip the first element
        .collect();

    let card_name = format!("{}/{}/v{}", names[0], names[1], names[2],);

    println!(
        "Downloading card artifacts for card {} to path {:?}",
        Colorize::purple(&card_name),
        Colorize::green(write_path.to_str().unwrap())
    );

    download_card_artifacts(&key, &write_path)?;

    Ok(())
}

pub fn download_service_from_registry(
    args: &CardQueryArgs,
    write_path: &Path,
) -> Result<(), RegistryError> {
    let registry = OpsmlRegistry::new(args.registry_type.clone())?;

    let key = registry.get_key(args)?;

    // delete directory if it exists
    if write_path.exists() {
        std::fs::remove_dir_all(write_path)?;
    }

    // download service card card
    download_card_artifacts(&key, write_path)?;

    // read Card.json file
    let service = ServiceCard::load_service_json(write_path).map_err(RegistryError::CardError)?;

    let service_name = format!("{}/{}/v{}", service.space, service.name, service.version);

    println!(
        "Downloading service card for card {} to path {}",
        Colorize::purple(&service_name),
        Colorize::green(write_path.to_str().unwrap())
    );

    let mut mapping = ServiceCardMapping::new();
    let current_dir = std::env::current_dir()?;

    // Download each card in the service
    service
        .cards
        .iter()
        .try_for_each(|card| -> Result<(), RegistryError> {
            let query_args = CardQueryArgs {
                uid: Some(card.uid.clone()),
                name: Some(card.name.clone()),
                space: Some(card.space.clone()),
                version: Some(card.version.clone()),
                registry_type: card.registry_type.clone(),
                ..Default::default()
            };

            let key = registry.get_key(&query_args)?;
            let card_path = write_path
                .strip_prefix(&current_dir)
                .unwrap_or(write_path)
                .join(&card.alias);

            // Download card artifacts
            download_card_artifacts(&key, &card_path)?;
            mapping.add_card_path(&card.alias, &card_path);

            // If modelcard or promptcard, load and process drift paths
            if card.registry_type == RegistryType::Model
                || card.registry_type == RegistryType::Prompt
            {
                let card_json_path = card_path.join(SaveName::Card).with_extension(Suffix::Json);
                let json_string = std::fs::read_to_string(&card_json_path)?;

                let drift_paths = match card.registry_type {
                    RegistryType::Model => {
                        let modelcard: ModelCard = serde_json::from_str(&json_string)?;
                        modelcard
                            .metadata
                            .interface_metadata
                            .save_metadata
                            .drift_profile_uri_map
                    }
                    RegistryType::Prompt => {
                        let promptcard: PromptCard = serde_json::from_str(&json_string)?;
                        promptcard.metadata.drift_profile_uri_map
                    }
                    _ => {
                        debug!(
                            "Card {} is not a ModelCard or PromptCard, skipping drift paths",
                            card.alias
                        );
                        None
                    }
                };

                match drift_paths {
                    Some(paths) => {
                        for (alias, path) in paths {
                            // create drift alias and path
                            // {card_path}/{uri} - uri is relative to parent card path in the profile uri map
                            let drift_path = card_path.join(path.uri);
                            mapping.add_drift_path(&alias, &drift_path);
                        }
                    }
                    None => {
                        debug!("{} has no drift paths", card.alias);
                    }
                }
                // Optionally: do something with drift_paths
            }
            Ok(())
        })?;

    // save mapping to card root dir
    let mapping_path = write_path
        .join(SaveName::CardMap)
        .with_extension(Suffix::Json);

    PyHelperFuncs::save_to_json(mapping, &mapping_path)?;

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (write_dir, space=None, name=None, version=None, uid=None))]
/// Helper function for downloading a service from the registry
/// # Arguments
/// * `write_dir` - The directory to write the downloaded service to
/// * `space` - The space the service belongs to
/// * `name` - The name of the service
/// * `version` - The version of the service
/// * `uid` - The unique identifier of the service
pub fn download_service(
    write_dir: PathBuf,
    space: Option<String>,
    name: Option<String>,
    version: Option<String>,
    uid: Option<String>,
) -> Result<(), RegistryError> {
    // convert to query args
    let query_args = CardQueryArgs {
        registry_type: RegistryType::Service,
        space,
        name,
        version,
        uid,
        ..Default::default()
    };

    // download service from registry
    download_service_from_registry(&query_args, &write_dir)?;

    Ok(())
}

/// Downloads a service card
async fn load_service_card(
    args: &CardQueryArgs,
    write_path: &Path,
    registry: &AsyncOpsmlRegistry,
) -> Result<ServiceCard, RegistryError> {
    let key = registry.get_key(args).await?;

    // delete directory if it exists
    if write_path.exists() {
        std::fs::remove_dir_all(write_path)?;
    }

    // download service card card
    async_download_card_artifacts(&key, write_path).await?;

    // read Card.json file
    let service = ServiceCard::load_service_json(write_path).map_err(RegistryError::CardError)?;
    let service_name = format!("{}/{}/v{}", service.space, service.name, service.version);

    println!(
        "Downloading service card for card {} to path {}",
        Colorize::purple(&service_name),
        Colorize::green(write_path.to_str().unwrap())
    );

    Ok(service)
}

/// Downloads a card to path
async fn async_download_card(
    card: &Card,
    write_path: &Path,
    registry: &AsyncOpsmlRegistry,
    current_dir: &Path,
    mapping: &mut ServiceCardMapping,
) -> Result<(), RegistryError> {
    let query_args = CardQueryArgs {
        uid: Some(card.uid.clone()),
        name: Some(card.name.clone()),
        space: Some(card.space.clone()),
        version: Some(card.version.clone()),
        registry_type: card.registry_type.clone(),
        ..Default::default()
    };

    let key = registry.get_key(&query_args).await?;
    let card_path = write_path
        .strip_prefix(current_dir)
        .unwrap_or(write_path)
        .join(&card.alias);

    // Download card artifacts
    async_download_card_artifacts(&key, &card_path).await?;
    mapping.add_card_path(&card.alias, &card_path);

    // check if card has drift profiles and add them to map
    if card.registry_type == RegistryType::Model || card.registry_type == RegistryType::Prompt {
        process_drift_paths(card, &card_path, mapping)?;
    }

    Ok(())
}

#[instrument(skip_all)]
async fn async_download_card_artifacts(
    key: &ArtifactKey,
    lpath: &Path,
) -> Result<(), RegistryError> {
    // get registry
    let decryption_key = key.get_decrypt_key()?;
    let rpath = key.storage_path();

    if !lpath.exists() {
        std::fs::create_dir_all(lpath)?;
    }
    // download card artifacts
    debug!("Downloading card artifacts from storage");
    async_storage_client()
        .await
        .get(lpath, &rpath, true)
        .await?;

    decrypt_directory(lpath, &decryption_key)?;

    Ok(())
}

/// Checks a card for drift paths and adds to mapping if they exist
fn process_drift_paths(
    card: &Card,
    card_path: &Path,
    mapping: &mut ServiceCardMapping,
) -> Result<(), RegistryError> {
    let card_json_path = card_path.join(SaveName::Card).with_extension(Suffix::Json);
    let json_string = std::fs::read_to_string(&card_json_path)?;

    let drift_paths = match card.registry_type {
        RegistryType::Model => {
            let modelcard: ModelCard = serde_json::from_str(&json_string)?;
            modelcard
                .metadata
                .interface_metadata
                .save_metadata
                .drift_profile_uri_map
        }
        RegistryType::Prompt => {
            let promptcard: PromptCard = serde_json::from_str(&json_string)?;
            promptcard.metadata.drift_profile_uri_map
        }
        _ => {
            debug!(
                "Card {} is not a ModelCard or PromptCard, skipping drift paths",
                card.alias
            );
            None
        }
    };

    if let Some(paths) = drift_paths {
        for (alias, path) in paths {
            // create drift alias and path
            // {card_path}/{uri} - uri is relative to parent card path in the profile uri map
            let drift_path = card_path.join(path.uri);
            mapping.add_drift_path(&alias, &drift_path);
        }
    } else {
        debug!("{} has no drift paths", card.alias);
    }

    Ok(())
}

/// Async equivalent of downloading a service from the registry
/// # Arguments
/// * `args` - The arguments for the card query
/// * `write_path` - The path to write the downloaded service
/// * `registry` - The async opsml registry
#[instrument(skip_all)]
pub async fn async_download_service_from_registry(
    args: &CardQueryArgs,
    write_path: &Path,
    registry: &AsyncOpsmlRegistry,
) -> Result<(), RegistryError> {
    // 1. Get the ServiceCard
    debug!("Downloading ServiceCard");
    let service = load_service_card(args, write_path, registry).await?;

    // 2. Create a mapping for the service card
    debug!("Creating mapping for ServiceCard");
    let mut mapping = ServiceCardMapping::new();
    let current_dir = std::env::current_dir()?;

    // 3. Download card
    debug!("Downloading cards");
    for card in &service.cards {
        async_download_card(card, write_path, registry, &current_dir, &mut mapping).await?;
    }

    // 4. Save mapping to card root dir
    debug!("Saving mapping to card root dir");
    let mapping_path = write_path
        .join(SaveName::CardMap)
        .with_extension(Suffix::Json);

    PyHelperFuncs::save_to_json(mapping, &mapping_path)?;

    Ok(())
}
