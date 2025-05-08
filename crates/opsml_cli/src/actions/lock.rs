use crate::actions::utils::register_card_deck;
use crate::cli::arg::DownloadCard;
use crate::download_deck;
use crate::error::CliError;
use opsml_colors::Colorize;
use opsml_registry::error::RegistryError;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_toml::{
    toml::{AppConfig, Card},
    LockArtifact, LockFile, PyProjectToml,
};
use opsml_types::{
    contracts::{CardEntry, CardRecord},
    RegistryType,
};
use pyo3::prelude::*;
use std::path::PathBuf;
use tracing::{debug, error, instrument};

/// Helper function to get cards from registry
fn get_deck_from_registry(
    registry: &CardRegistry,
    config: &AppConfig,
) -> Result<Option<CardRecord>, CliError> {
    let cards = registry.list_cards(
        None,
        Some(config.space.clone()),
        Some(config.name.clone()),
        config.version.clone(),
        None,
        None,
        Some(true),
        1,
    )?;
    Ok(cards.cards.first().cloned())
}

/// Helper function to validate app configuration
fn validate_app_cards(config: &AppConfig) -> Result<&Vec<Card>, CliError> {
    config.cards.as_ref().ok_or(CliError::MissingDeckCards)
}

/// Helper function to get latest card from appropriate registry
///
/// # Arguments
/// * `registries` - RustRegistries
/// * `entry` - DeckCard
///
/// # Returns
/// * `Result<CardRecord, CliError>` - The latest card record
///
/// # Errors
/// * `CliError::MissingRegistryType` - If the registry type is missing
fn get_latest_card(registries: &CardRegistries, card: &Card) -> Result<CardRecord, CliError> {
    // extract registry type from entry
    let registry_type = card.registry_type.clone();

    let registry = match registry_type {
        RegistryType::Model => &registries.model,
        RegistryType::Experiment => &registries.experiment,
        RegistryType::Data => &registries.data,
        RegistryType::Prompt => &registries.prompt,
        RegistryType::Deck => &registries.deck,
        _ => return Err(RegistryError::RegistryTypeNotSupported(registry_type).into()),
    };

    let latest_cards = registry.list_cards(
        None,
        Some(card.space.clone()),
        Some(card.name.clone()),
        card.version.clone(),
        None,
        None,
        Some(false),
        1,
    )?;

    // return the first card in the list
    latest_cards.cards.first().cloned().ok_or({
        error!("Failed to get latest card");
        CliError::MissingCardError
    })
}

/// Process deck cards and check for version updates
///
/// # Arguments
/// * `card_entries` - Vec<CardEntry> - List of cards associated with the most recent registered deck
/// * `app_cards` - &[DeckCard] - List of cards found in toml
/// * `registries` - &RustRegistries - Rust variant of Opsml registries
///
/// # Returns
/// * `Result<bool, CliError>` - True if a version refresh is needed, false otherwise
#[instrument(skip_all)]
fn process_deck_cards(
    card_entries: Vec<CardEntry>,
    app_cards: &[Card],
    registries: &CardRegistries,
) -> Result<bool, CliError> {
    debug!("Processing deck cards");
    for app_card in app_cards {
        // Find the latest card given the constraints provided in toml file
        let latest_card = get_latest_card(registries, app_card)?;

        // Find the entry in the card entries
        // If the entry is not found - return true (need to increment version)
        // If the entry is found - check if the uid is different from latest card - if different - return true
        // Otherwise - return false
        // Find matching entry in existing deck
        let existing_entry = card_entries
            .iter()
            .find(|entry| entry.alias == app_card.alias);

        match existing_entry {
            Some(entry) => {
                // Check if existing entry UID matches latest card UID
                if entry.uid != latest_card.uid() {
                    return Ok(true);
                }
            }
            // No existing entry found - needs refresh
            None => return Ok(true),
        }
    }

    Ok(false)
}

/// create lock entry for a deck
/// # Arguments
/// * `config` - AppConfig
fn lock_deck(config: AppConfig) -> Result<LockArtifact, CliError> {
    debug!("Locking deck with config: {:?}", config);

    // Validate app configuration
    let app_cards = validate_app_cards(&config)?;
    let registries = CardRegistries::new()?;

    // Initialize registry and get deck
    let deck = get_deck_from_registry(&registries.deck, &config)?;

    // Handle deck creation if it doesn't exist
    if deck.is_none() {
        let card = register_card_deck(&config, &registries.deck)?;
        return Ok(LockArtifact {
            space: card.space.clone(),
            name: card.name.clone(),
            version: card.version.clone(),
            uid: card.uid.clone(),
            registry_type: RegistryType::Deck,
            write_dir: config.write_dir.unwrap_or("opsml_app".to_string()),
        });
    }
    //
    //// Process existing deck
    let deck = deck.unwrap();
    //
    //// Get card UIDs from deck
    let card_entries = deck.cards().ok_or(CliError::MissingCardEntriesError)?;
    let needs_refresh = process_deck_cards(card_entries, app_cards, &registries)?;
    //
    let lock_entry = match needs_refresh {
        true => {
            // If refresh is needed, register the deck again
            let card = register_card_deck(&config, &registries.deck)?;
            LockArtifact {
                space: card.space.clone(),
                name: card.name.clone(),
                version: card.version.clone(),
                uid: card.uid.clone(),
                registry_type: RegistryType::Deck,
                write_dir: config.write_dir.unwrap_or("opsml_app".to_string()),
            }
        }
        false => {
            // No refresh needed, return existing entry
            LockArtifact {
                space: deck.space().to_string(),
                name: deck.name().to_string(),
                version: deck.version().to_string(),
                uid: deck.uid().to_string(),
                registry_type: RegistryType::Deck,
                write_dir: config.write_dir.unwrap_or("opsml_app".to_string()),
            }
        }
    };

    Ok(lock_entry)
}

/// Create the the lock file for the app
fn lock_app(app: AppConfig) -> Result<LockArtifact, CliError> {
    // Create a lock file for the app
    // Only support's  deck currently
    match app.registry_type {
        RegistryType::Deck => lock_deck(app),
        _ => Err(RegistryError::RegistryTypeNotSupported(app.registry_type).into()),
    }
}

#[pyfunction]
#[pyo3(signature = (path, write_path=None))]
pub fn install_app(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> {
    debug!("Installing app from lock file");

    println!("{}", Colorize::green("Downloading app for opsml.lock file"));

    let lockfile = LockFile::read(&path)?;

    for artifact in lockfile.artifact {
        match artifact.registry_type {
            RegistryType::Deck => {
                println!(
                    "Downloading CardDeck {} to path {}",
                    Colorize::green(&format!(
                        "{}/{}/v{}",
                        &artifact.name, &artifact.space, &artifact.version
                    )),
                    Colorize::purple(&artifact.write_dir),
                );

                let write_path = if let Some(path) = write_path.as_ref() {
                    path.to_path_buf()
                } else {
                    let current_dir = std::env::current_dir()?;
                    // Store the `PathBuf` in a variable and return a reference to it
                    current_dir.as_path().to_path_buf()
                };

                let args = DownloadCard {
                    space: Some(artifact.space.clone()),
                    name: Some(artifact.name.clone()),
                    version: Some(artifact.version.clone()),
                    uid: Some(artifact.uid.clone()),
                    write_dir: write_path
                        .join(artifact.write_dir)
                        .into_os_string()
                        .into_string()
                        .map_err(|_| CliError::WritePathError)?,
                };

                download_deck(&args)?;
            }
            _ => {
                return Err(RegistryError::RegistryTypeNotSupported(artifact.registry_type).into());
            }
        }
    }

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (path=None, toml_name=None))]
pub fn lock_project(path: Option<PathBuf>, toml_name: Option<&str>) -> Result<(), CliError> {
    debug!("Locking project with path: {:?}", path);

    let pyproject = PyProjectToml::load(path.as_deref(), toml_name)?;

    let tools = pyproject.get_tools().ok_or(CliError::MissingToolsError)?;

    let apps = tools.get_apps().ok_or(CliError::MissingAppError)?;

    // Create a lock file
    let lock_file = LockFile {
        artifact: apps
            .iter()
            .map(|app| lock_app(app.clone()))
            .collect::<Result<Vec<_>, _>>()?,
    };

    lock_file.write(&pyproject.root_path)?;

    Ok(())
}
