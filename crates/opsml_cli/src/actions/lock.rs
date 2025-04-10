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
    config.cards.as_ref().ok_or(CliError::Error(
        "No cards found in the app config. An app config must be present".to_string(),
    ))
}

/// Helper function to get latest card from appropriate registry
fn get_latest_card(registries: &RustRegistries, entry: &CardEntry) -> Result<CardRecord, CliError> {
    let query_args = CardQueryArgs {
        uid: Some(entry.uid.clone()),
        registry_type: entry.registry_type.clone(),
        sort_by_timestamp: Some(true),
        limit: Some(1),
        ..Default::default()
    };

    let latest_cards = match entry.registry_type {
        RegistryType::Model => registries.model.list_cards(query_args)?,
        RegistryType::Experiment => registries.experiment.list_cards(query_args)?,
        RegistryType::Data => registries.data.list_cards(query_args)?,
        RegistryType::Audit => registries.audit.list_cards(query_args)?,
        RegistryType::Prompt => registries.prompt.list_cards(query_args)?,
        _ => {
            return Err(CliError::Error(format!(
                "Unsupported registry type: {}",
                entry.registry_type
            )))
        }
    };

    latest_cards
        .first()
        .cloned()
        .ok_or_else(|| CliError::Error(format!("No card found for uid: {}", entry.uid)))
}

fn needs_version_refresh(version: &str) -> bool {
    version.contains('*') || version.contains('^') || version.contains('~')
}

/// Process deck cards and check for version updates
fn process_deck_cards(
    card_entries: Vec<CardEntry>,
    app_cards: &[DeckCard],
    registries: &RustRegistries,
) -> Result<bool, CliError> {
    for entry in card_entries {
        let latest_card = get_latest_card(registries, &entry)?;

        if latest_card.version() != entry.version {
            if let Some(app_card) = app_cards.iter().find(|c| c.alias == entry.alias) {
                if let Some(version) = &app_card.version {
                    if needs_version_refresh(version) {
                        return Ok(true);
                    }
                }
            }
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
    let card_entries = deck
        .card_uids()
        .ok_or(CliError::Error("No card UIDs found in deck".to_string()))?;

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
