// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{Card, ServiceCard};
pub use opsml_registry::utils::validate_service_cards;
use opsml_registry::CardRegistry;
use opsml_semver::VersionType;
use opsml_toml::toml::ServiceConfig;

/// Create a new service card from an app configuration
///
/// # Arguments
/// * `app` - DeckConfig
///
/// # Returns
/// Result<ServiceCard, CliError>
///
/// # Errors
/// CliError if:
/// * The app configuration is invalid
/// * The cards in the app configuration are invalid
/// * The service card cannot be created
pub fn create_service_card(app: &ServiceConfig) -> Result<ServiceCard, CliError> {
    // extract cards into Vec<Card>

    let mut cards = app
        .cards
        .as_ref()
        .ok_or(CliError::MissingServiceCards)?
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
    validate_service_cards(&mut cards)?;

    // Create a new service card
    ServiceCard::rust_new(
        app.space.clone(),
        app.name.clone(),
        cards,
        app.version.as_deref(),
    )
    .map_err(CliError::CreateServiceError)
}

pub fn register_service_card(
    config: &ServiceConfig,
    registry: &CardRegistry,
) -> Result<ServiceCard, CliError> {
    // Validate the app configuration
    let mut service = create_service_card(config)?;
    registry.register_card_rs(&mut service, VersionType::Minor)?;

    Ok(service)
}
