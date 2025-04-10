use opsml_cards::Card;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
use opsml_toml::{tools::AppConfig, OpsmlTool, OpsmlTools, PyProjectToml};
use opsml_types::{contracts::CardQueryArgs, RegistryType};
use serde::{Deserialize, Serialize};

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

/// create lock entry for a deck
/// # Arguments
/// * `deck` - AppConfig
async fn lock_deck(config: AppConfig) -> Result<(), CliError> {
    // Create a lock entry for the deck

    // check if the deck already exists
    let registry = OpsmlRegistry::new(config.registry_type.clone())?;

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

    if cards.is_empty() && config.create {
        unimplemented!("Create a new deck");
        return Ok(());
    }

    // get the first card
    let card = cards
        .first()
        .ok_or_else(|| CliError::Error(format!("No card found")))?;

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
