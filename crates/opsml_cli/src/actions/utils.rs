// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{Card, ServiceCard};
pub use opsml_registry::utils::validate_service_cards;
use opsml_registry::CardRegistry;
use opsml_semver::VersionType;
use opsml_service::ServiceSpec;

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
pub fn create_service_card(
    spec: &ServiceSpec,
    space: &str,
    name: &str,
) -> Result<ServiceCard, CliError> {
    // if service_type is MCP and no cards are defined, create default MCP cards
    let cards = match spec.service_type {
        opsml_types::contracts::ServiceType::Mcp if spec.service.cards.is_none() => Vec::new(),
        _ => {
            let mut cards = spec
                .service
                .cards
                .as_ref()
                .ok_or(CliError::MissingServiceCards)?
                .iter()
                .map(|card| {
                    Card::rust_new(
                        card.alias.clone(),
                        card.registry_type.clone(),
                        card.space.clone(),
                        card.name.clone(),
                        card.version.clone(),
                    )
                })
                .collect::<Vec<_>>();

            validate_service_cards(&mut cards)?;
            cards
        }
    };

    // Create a new service card
    ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)
}

pub fn register_service_card(
    spec: &ServiceSpec,
    registry: &CardRegistry,
    space: &str,
    name: &str,
) -> Result<ServiceCard, CliError> {
    // Validate the app configuration
    let mut service = create_service_card(spec, space, name)?;
    registry.register_card_rs(&mut service, VersionType::Minor)?;

    Ok(service)
}
