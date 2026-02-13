// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{PromptCard, ServiceCard};
use opsml_registry::CardRegistry;
pub use opsml_registry::utils::validate_service_cards;
use opsml_semver::VersionType;
use opsml_service::ServiceSpec;
use opsml_types::RegistryType;
use opsml_types::contracts::Card;
use std::path::Path;
use tracing::{debug, warn};

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
    card: &mut Card,
    root_path: &Path,
    registry: &CardRegistry,
) -> Result<(), CliError> {
    // this is already checked before calling this function, but we check again here to be safe
    let path_str = card
        .path
        .as_ref()
        .ok_or_else(|| CliError::Error("Prompt card path is missing".to_string()))?;

    debug!(
        "Loading PromptCard from path: {} for alias: {}",
        card.path.as_ref().unwrap_or(&"".to_string()),
        card.alias
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

    // Check if content hash matches registry to avoid unnecessary registration and versioning if content is the same
    if let Ok(true) = registry.compare_card_hash(prompt_card.calculate_content_hash()?.as_slice()) {
        warn!(
            "PromptCard content hash matches registry, skipping registration for: {}/{}",
            card.space, card.name
        );
    } else {
        // Register the PromptCard
        registry
            .register_card_rs(
                &mut prompt_card,
                card.version_type // maybe move this as default in spec later on
                    .as_ref()
                    .unwrap_or(&VersionType::Minor)
                    .clone(),
            )
            .map_err(|e| CliError::Error(format!("Failed to register PromptCard: {}", e)))?;

        debug!(
            "Registered PromptCard: {}/{} version {} (uid: {})",
            card.space, card.name, prompt_card.version, prompt_card.uid
        );
    }

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
                    card.version_type.clone(),
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

/// Attempts to register a service card based on the provided spec.
/// Flow:
/// 1. Iterate through cards in spec. If any cards/prompts have paths, load them and register them first.
/// 2. Validate the cards in the spec after loading any cards from paths to ensure they are valid before registering the service card.
/// 3. Create the service card and calculate its content hash.
/// 4. Check the content hash against the registry - if it matches, skip registration to avoid creating a new version with the same content.
///    If it doesn't match, register the service card
pub fn register_service_card(
    spec: &mut ServiceSpec,
    registry: &CardRegistry,
    space: &str,
    name: &str,
) -> Result<(ServiceCard, bool), CliError> {
    if let Some(service_config) = &mut spec.service
        && let Some(cards) = &mut service_config.cards
    {
        for card in cards.iter_mut() {
            if card.registry_type == RegistryType::Prompt && card.path.is_some() {
                process_prompt_card_from_path(card, &spec.root_path, registry)?;
            }
        }
        validate_service_cards(cards)?;
    }

    let cards = spec
        .service
        .as_ref()
        .and_then(|s| s.cards.as_ref())
        .cloned()
        .unwrap_or_default();

    let mut service = ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)?;

    // check service content hash against registry to avoid unnecessary registration and versioning if content is the same
    if let Ok(true) = registry.compare_card_hash(service.calculate_content_hash()?.as_slice()) {
        warn!(
            "ServiceCard content hash matches registry, skipping registration for: {}/{}",
            space, name
        );
        return Ok((service, false));
    }

    registry.register_card_rs(&mut service, VersionType::Minor)?;

    Ok((service, true))
}
