use opsml_cards::Card;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
use opsml_registry::RustRegistries;
use opsml_toml::tools::DeckCard;
use opsml_toml::{tools::AppConfig, OpsmlTool, OpsmlTools, PyProjectToml};
use opsml_types::{
    contracts::{CardEntry, CardQueryArgs, CardRecord},
    RegistryType,
};
use serde::{Deserialize, Serialize};

use crate::cli::Cli;

#[derive(Debug, Serialize, Deserialize)]
pub struct LockEntry {
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub registry_type: RegistryType,
}

/// LockFile struct to hold the lock entries
pub struct LockFile {
    // Each entry is considered a service
    pub service: Vec<LockEntry>,
}

/// create lock entry for a card
/// # Arguments
/// * `card` - AppConfig
async fn lock_card(config: AppConfig) -> Result<(), CliError> {
    // Create a lock file for the card
    //let registry_type = card.registry_type;
    Ok(())
}

/// Helper function to get cards from registry
fn get_deck_from_registry(
    registry: &OpsmlRegistry,
    config: &AppConfig,
) -> Result<Option<CardRecord>, CliError> {
    let query_args = CardQueryArgs {
        space: config.space.clone(),
        name: config.name.clone(),
        version: config.version.clone(),
        uid: config.uid.clone(),
        registry_type: config.registry_type.clone(),
        limit: Some(1),
        ..Default::default()
    };

    let cards = registry.list_cards(query_args)?;
    Ok(cards.first().cloned())
}

/// Helper function to validate app configuration
fn validate_app_cards(config: &AppConfig) -> Result<&Vec<DeckCard>, CliError> {
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
fn get_latest_card(registries: &RustRegistries, card: &DeckCard) -> Result<CardRecord, CliError> {
    // extract registry type from entry
    let registry_type = card
        .registry_type
        .as_ref()
        .ok_or(CliError::MissingRegistryType)?;

    // set args for querying registry
    let query_args = CardQueryArgs {
        space: card.space.clone(),
        name: card.name.clone(),
        version: card.version.clone(),
        uid: card.uid.clone(),
        registry_type: registry_type.clone(),
        sort_by_timestamp: Some(true),
        limit: Some(1),
        ..Default::default()
    };

    // get the latest card from the appropriate registry
    let latest_cards = match registry_type {
        RegistryType::Model => registries.model.list_cards(query_args)?,
        RegistryType::Experiment => registries.experiment.list_cards(query_args)?,
        RegistryType::Data => registries.data.list_cards(query_args)?,
        RegistryType::Audit => registries.audit.list_cards(query_args)?,
        RegistryType::Prompt => registries.prompt.list_cards(query_args)?,
        _ => {
            return Err(CliError::RegistryTypeNotSupported(
                registry_type.to_string(),
            ))
        }
    };

    // return the first card in the list
    latest_cards
        .first()
        .cloned()
        .ok_or(CliError::MissingCardRecord)
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
fn process_deck_cards(
    card_entries: Vec<CardEntry>,
    app_cards: &[DeckCard],
    registries: &RustRegistries,
) -> Result<bool, CliError> {
    for app_card in app_cards {
        // Find the latest card given the constraints provided in toml file
        let latest_card = get_latest_card(registries, &app_card)?;

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
/// * `deck` - AppConfig
/// create lock entry for a deck
async fn lock_deck(config: AppConfig) -> Result<(), CliError> {
    // Validate app configuration
    let app_cards = validate_app_cards(&config)?;
    let registries = RustRegistries::new()?;

    // Initialize registry and get deck
    let deck = get_deck_from_registry(&registries.deck, &config)?;

    // Handle deck creation if it doesn't exist
    if deck.is_none() {
        if config.create {
            unimplemented!("Create a new deck");
        }
        return Ok(());
    }

    // Process existing deck
    let deck = deck.unwrap();

    // Get card UIDs from deck
    let card_entries = deck.card_uids().ok_or(CliError::MissingCardDeckUids)?;
    let needs_refresh = process_deck_cards(card_entries, app_cards, &registries)?;

    Ok(())
}

/// Create the the lock file for the app
async fn lock_app(app: AppConfig) -> Result<(), CliError> {
    // Create a lock file for the app
    match app.registry_type {
        RegistryType::Model => lock_card(app).await?,
        RegistryType::Experiment => lock_card(app).await?,
        RegistryType::Data => lock_card(app).await?,
        RegistryType::Audit => lock_card(app).await?,
        RegistryType::Prompt => lock_card(app).await?,
        RegistryType::Deck => lock_deck(app).await?,
        _ => {
            return Err(CliError::Error(
                "Unsupported registry type for lock file".to_string(),
            ))
        }
    }

    Ok(())
}

pub async fn lock() -> Result<(), CliError> {
    // Load the pyproject.toml file
    let pyproject = PyProjectToml::load(None)?;

    let tools = match pyproject.get_tools() {
        Some(config) => config,
        None => {
            return Err(CliError::Error(
                "No tools found in pyproject.toml. An tool config must be present".to_string(),
            ));
        }
    };

    let apps = match tools.get_apps() {
        Some(apps) => apps.clone(),
        None => {
            return Err(CliError::Error(
                "No apps found in pyproject.toml. An app config must be present".to_string(),
            ));
        }
    };

    Ok(())
}
