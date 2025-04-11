use crate::cli::arg::DownloadCard;
use crate::cli::arg::IntoQueryArgs;
use opsml_cards::CardDeck;
use opsml_colors::Colorize;
use opsml_crypt::decrypt_directory;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
use opsml_storage::storage_client;
use opsml_types::contracts::ArtifactKey;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::RegistryType;
use std::path::Path;

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
        std::fs::create_dir_all(lpath).map_err(|e| CliError::Error(format!("{}", e)))?;
    }
    // download card artifacts
    storage_client()
        .map_err(|e| CliError::Error(format!("{}", e)))?
        .get(lpath, &rpath, true)
        .map_err(|e| CliError::Error(format!("{}", e)))?;

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

    let key = registry.get_key(query_args)?;

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

    let key = registry.get_key(query_args)?;
    let base_path = args.deck_path();

    // delete directory if it exists
    if base_path.exists() {
        std::fs::remove_dir_all(&base_path).map_err(CliError::DeleteBasePathError)?;
    }

    // download card deck card
    download_card_artifacts(&key, &base_path)?;

    // read Card.json file
    let card_deck = CardDeck::load_card_deck_json(&base_path)
        .map_err(|e| CliError::Error(format!("Failed to load card deck JSON file: {}", e)))?;

    let card_deck_name = format!(
        "{}/{}/v{}",
        card_deck.space, card_deck.name, card_deck.version
    );

    println!(
        "Downloading card deck for card {} to path {}",
        Colorize::purple(&card_deck_name),
        Colorize::green(&args.write_dir)
    );

    // Use try_for_each instead of for_each to handle Results
    card_deck.cards.into_iter().try_for_each(|card| {
        let query_args = CardQueryArgs {
            uid: Some(card.uid.clone()),
            name: Some(card.name.clone()),
            space: Some(card.space.clone()),
            version: Some(card.version.clone()),
            registry_type: card.registry_type.clone(),
            ..Default::default()
        };

        let key = registry.get_key(query_args)?;
        let card_path = base_path.join(&card.alias);

        // download card artifacts
        download_card_artifacts(&key, &card_path)
    })?;

    Ok(())
}
