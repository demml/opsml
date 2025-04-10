// This module contains utility functions for the opsml_cli crate.
use opsml_cards::{Card, CardDeck, CardList};
use opsml_error::CliError;
pub use opsml_registry::utils::validate_card_deck;
use opsml_toml::tools::AppConfig;

pub fn create_card_deck(app: AppConfig) -> Result<(), CliError> {
    // extract cards into Vec<Card>

    let cards = app
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
            Ok(card)
        })
        .collect::<Result<Vec<_>, _>>()?;

    // Validate the app configuration
    CardDeck::new(app.space, app.name, cards, app.version)?;

    Ok(())
}
