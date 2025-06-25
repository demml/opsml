use crate::cli::arg::DownloadCard;
use crate::cli::arg::IntoQueryArgs;
use crate::error::CliError;
use opsml_cards::CardDeck;
use opsml_cards::ModelCard;
use opsml_colors::Colorize;
use opsml_crypt::decrypt_directory;
use opsml_registry::base::OpsmlRegistry;
use opsml_storage::storage_client;
use opsml_types::{
    cards::CardDeckMapping,
    contracts::{ArtifactKey, CardQueryArgs},
    RegistryType, SaveName, Suffix,
};
use opsml_utils::PyHelperFuncs;
use std::path::Path;
use tracing::debug;
/// Download all artifacts of a card
///
/// # Arguments
/// * `key` - ArtifactKey
/// * `write_dir` - str
///
/// # Returns
///
/// Result<(), CliError>
fn download_card_artifacts(key: &ArtifactKey, lpath: &Path) -> Result<(), CliError> {
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
/// CliError
pub fn download_card(args: &DownloadCard, registry_type: RegistryType) -> Result<(), CliError> {
    // convert to query args
    let query_args = args.into_query_args(registry_type)?;

    // get registry
    let registry = OpsmlRegistry::new(query_args.registry_type.clone())?;

    // Steps:
    // 1. Load the CardDeck from the registry
    // 2. Get all cards in the deck
    // 3. For each card, get the ArtifactKey, download the artifacts, and decrypt them
    // 4. Save the artifacts to the specified directory

    let key = registry.get_key(&query_args)?;

    let names: Vec<&str> = key
        .storage_key
        .split('/')
        .skip(1) // Skip the first element
        .collect();

    let card_name = format!("{}/{}/v{}", names[0], names[1], names[2],);

    println!(
        "Downloading card artifacts for card {} to path {}",
        Colorize::purple(&card_name),
        Colorize::green(&args.write_dir)
    );

    download_card_artifacts(&key, &args.write_path())?;

    Ok(())
}

pub fn download_deck(args: &DownloadCard) -> Result<(), CliError> {
    // convert to query args
    let query_args = args.into_query_args(RegistryType::Deck)?;

    // get registry
    let registry = OpsmlRegistry::new(query_args.registry_type.clone())?;

    let key = registry.get_key(&query_args)?;
    let base_path = args.deck_path();

    // delete directory if it exists
    if base_path.exists() {
        std::fs::remove_dir_all(&base_path)?;
    }

    // download card deck card
    download_card_artifacts(&key, &base_path)?;

    // read Card.json file
    let card_deck =
        CardDeck::load_card_deck_json(&base_path).map_err(CliError::LoadCardDeckError)?;

    let card_deck_name = format!(
        "{}/{}/v{}",
        card_deck.space, card_deck.name, card_deck.version
    );

    println!(
        "Downloading card deck for card {} to path {}",
        Colorize::purple(&card_deck_name),
        Colorize::green(&args.write_dir)
    );

    let mut mapping = CardDeckMapping::new();
    let current_dir = std::env::current_dir()?;

    // Download each card in the deck
    card_deck
        .cards
        .iter()
        .try_for_each(|card| -> Result<(), CliError> {
            let query_args = CardQueryArgs {
                uid: Some(card.uid.clone()),
                name: Some(card.name.clone()),
                space: Some(card.space.clone()),
                version: Some(card.version.clone()),
                registry_type: card.registry_type.clone(),
                ..Default::default()
            };

            let key = registry.get_key(&query_args)?;
            let card_path = base_path
                .strip_prefix(&current_dir)
                .unwrap_or(&base_path)
                .join(&card.alias);

            // Download card artifacts
            download_card_artifacts(&key, &card_path)?;
            mapping.add_card_path(&card.alias, &card_path);

            // If model card, load and process drift paths
            if card.registry_type == RegistryType::Model {
                let card_json_path = card_path.join(SaveName::Card).with_extension(Suffix::Json);
                let json_string = std::fs::read_to_string(&card_json_path)?;
                let modelcard: ModelCard = serde_json::from_str(&json_string)?;

                let drift_paths = modelcard
                    .metadata
                    .interface_metadata
                    .save_metadata
                    .drift_profile_uri_map;

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
                        debug!("ModelCard {} has no drift paths", card.alias);
                    }
                }
                // Optionally: do something with drift_paths
            }
            Ok(())
        })?;

    // save mapping to card root dir
    let mapping_path = base_path
        .join(SaveName::CardMap)
        .with_extension(Suffix::Json);

    PyHelperFuncs::save_to_json(mapping, &mapping_path)?;

    Ok(())
}
