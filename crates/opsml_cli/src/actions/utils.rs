// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{Card, CardDeck};
pub use opsml_registry::utils::validate_card_deck_cards;
use opsml_registry::CardRegistry;
use opsml_semver::VersionType;
use opsml_toml::toml::DeckConfig;

/// Create a new card deck from an app configuration
///
/// # Arguments
/// * `app` - DeckConfig
///
/// # Returns
/// Result<CardDeck, CliError>
///
/// # Errors
/// CliError if:
/// * The app configuration is invalid
/// * The cards in the app configuration are invalid
/// * The card deck cannot be created
pub fn create_card_deck(app: &DeckConfig) -> Result<CardDeck, CliError> {
    // extract cards into Vec<Card>

    let mut cards = app
        .cards
        .as_ref()
        .ok_or(CliError::MissingDeckCards)?
        .iter()
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
    CardDeck::rust_new(
        app.space.clone(),
        app.name.clone(),
        cards,
        app.version.as_deref(),
    )
    .map_err(CliError::CreateDeckError)
}

pub fn register_card_deck(
    config: &DeckConfig,
    registry: &CardRegistry,
) -> Result<CardDeck, CliError> {
    // Validate the app configuration
    let mut card_deck = create_card_deck(config)?;
    registry.register_card_rs(&mut card_deck, VersionType::Minor)?;

    Ok(card_deck)
}
