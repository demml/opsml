// This module contains utility functions for the opsml_cli crate.
use opsml_cards::{Card, CardDeck, CardList};
use opsml_colors::Colorize;
use opsml_error::CliError;
use opsml_registry::base::OpsmlRegistry;
pub use opsml_registry::utils::validate_card_deck_cards;
use opsml_semver::VersionType;
use opsml_toml::tools::AppConfig;
use opsml_types::contracts::card;
use opsml_types::{CommonKwargs, RegistryType};

/// Create a new card deck from an app configuration
///
/// # Arguments
/// * `app` - AppConfig
///
/// # Returns
/// Result<CardDeck, CliError>
///
/// # Errors
/// CliError if:
/// * The app configuration is invalid
/// * The cards in the app configuration are invalid
/// * The card deck cannot be created
pub fn create_card_deck(app: AppConfig) -> Result<CardDeck, CliError> {
    // extract cards into Vec<Card>

    let mut cards = app
        .cards
        .as_ref()
        .ok_or(CliError::MissingDeckCards)?
        .into_iter()
        .map(|card| {
            let card = Card::rust_new(
                card.alias.clone(),
                card.registry_type.clone(),
                card.space.clone(),
                card.name.clone(),
                card.version.clone(),
            );
            Ok::<_, CliError>(card)
        })
        .collect::<Result<Vec<_>, _>>()?;

    // Validate the cards
    validate_card_deck_cards(&mut cards)?;

    // Create a new card deck
    CardDeck::rust_new(app.space, app.name, cards, app.version.as_deref())
        .map_err(|e| CliError::CreateDeckError(e))
}

pub fn register_card_deck(app: AppConfig, registry: &OpsmlRegistry) -> Result<(), CliError> {
    // Validate the app configuration
    let card_deck = create_card_deck(app.clone())?;
    let registry_card = card_deck.get_registry_card()?;

    let version: Option<String> = if card_deck.version == CommonKwargs::BaseVersion.to_string() {
        None
    } else {
        Some(card_deck.version.clone())
    };

    let response = registry.create_card(registry_card, version, VersionType::Minor, None, None)?;

    println!(
        "{} - {} - {}/{} - v{}",
        Colorize::green("Registered card"),
        Colorize::purple(&app.registry_type.to_string()),
        response.space,
        response.name,
        response.version
    );

    // Register the card deck

    Ok(())
}
