// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{PromptCard, ServiceCard};
pub use opsml_registry::utils::validate_service_cards;
use opsml_registry::CardRegistry;
use opsml_semver::VersionType;
use opsml_service::ServiceSpec;
use opsml_types::contracts::Card;
use opsml_types::RegistryType;
use opsml_types::RegistryType;
use std::path::Path;
use std::path::Path;
use tracing::debug;
use tracing::debug;

/// Process prompt cards that have paths specified, loading and registering them
///
/// # Arguments
/// * `cards` - Mutable reference to cards vector
/// * `root_path` - Root path of the service spec for resolving relative paths
/// * `registry` - Card registry for registration
///
/// # Returns
/// Result with unit or CliError
///
/// # Errors
/// CliError if:
/// * The prompt card cannot be loaded from path
/// * The prompt card cannot be registered
pub fn process_prompt_card_from_path(
    cards: &mut Card,
    root_path: &Path,
    registry: &CardRegistry,
) -> Result<(), CliError> {
    debug!(
        "Loading PromptCard from path: {} for alias: {}",
        path_str, card.alias
    );

    // Resolve path relative to root_path if not absolute
    let card_path = if Path::new(path_str).is_absolute() {
        Path::new(path_str).to_path_buf()
    } else {
        root_path.join(path_str)
    };

    // Load the PromptCard from the specified path
    let mut prompt_card = PromptCard::from_path(card_path)
        .map_err(|e| CliError::Error(format!("Failed to load PromptCard: {}", e)))?;

    // Register the PromptCard
    registry
        .register_card_rs(&mut prompt_card, VersionType::Minor)
        .map_err(|e| CliError::Error(format!("Failed to register PromptCard: {}", e)))?;

    debug!(
        "Registered PromptCard: {}/{} version {} (uid: {})",
        card.space, card.name, prompt_card.version, prompt_card.uid
    );

    card.space = prompt_card.space;
    card.name = prompt_card.name;
    card.version = Some(prompt_card.version);
    card.uid = Some(prompt_card.uid);
    card.path = None;

    Ok(())
}

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
    let cards = if spec.service.is_none()
        || spec
            .service
            .as_ref()
            .and_then(|s| s.cards.as_ref())
            .is_none()
    {
        Vec::new()
    } else {
        let mut cards = spec
            .service
            .as_ref()
            .and_then(|s| s.cards.as_ref())
            .ok_or(CliError::MissingServiceCards)?
            .iter()
            .map(|card| {
                Card::rust_new(
                    card.alias.clone(),
                    card.registry_type.clone(),
                    card.space.clone(),
                    card.name.clone(),
                    card.version.clone(),
                    card.uid.clone(),
                    card.drift.clone(),
                )
            })
            .collect::<Vec<_>>();

        validate_service_cards(&mut cards)?;
        cards
    };

    // Create a new service card
    ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)
}

pub fn register_service_card(
    spec: &mut ServiceSpec,
    registry: &CardRegistry,
    space: &str,
    name: &str,
) -> Result<ServiceCard, CliError> {
    if let Some(service_config) = &mut spec.service {
        if let Some(cards) = &mut service_config.cards {
            for card in cards.iter_mut() {
                if card.registry_type == RegistryType::Prompt && card.path.is_some() {
                    process_prompt_card_from_path(card, &spec.root_path, registry)?;
                }
            }
            validate_service_cards(cards)?;
        }
    }

    let cards = spec
        .service
        .as_ref()
        .and_then(|s| s.cards.as_ref())
        .cloned()
        .unwrap_or_default();

    let mut service = ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)?;

    registry.register_card_rs(&mut service, VersionType::Minor)?;

    Ok(service)
}
