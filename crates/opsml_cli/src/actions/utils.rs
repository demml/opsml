// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{PromptCard, ServiceCard};
pub use opsml_registry::utils::validate_service_cards;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_semver::VersionType;
use opsml_service::OpsmlServiceSpec;
use opsml_types::contracts::Card;
use opsml_types::{RegistryType, contracts::CardVariant};
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
    card: &mut CardVariant,
    root_path: &Path,
    registry: &CardRegistry,
) -> Result<(), CliError> {
    let CardVariant::Path(card_path_variant) = card else {
        return Err(CliError::ExpectedCardPathVariant);
    };

    let card_path = if !card_path_variant.path.is_absolute() {
        root_path.join(&card_path_variant.path)
    } else {
        card_path_variant.path.clone()
    };

    debug!(
        "Loading PromptCard from path: {:?} for alias: {}",
        card_path, card_path_variant.alias
    );

    let mut prompt_card = PromptCard::from_path(card_path)
        .map_err(|e| CliError::Error(format!("Failed to load PromptCard: {}", e)))?;

    if let Ok(true) = registry.compare_card_hash(prompt_card.calculate_content_hash()?.as_slice()) {
        warn!(
            "PromptCard content hash matches registry, skipping registration for: {}/{}",
            prompt_card.space, prompt_card.name
        );
    } else {
        registry
            .register_card_rs(
                &mut prompt_card,
                card_path_variant
                    .version_type
                    .as_ref()
                    .unwrap_or(&VersionType::Minor)
                    .clone(),
            )
            .map_err(|e| CliError::Error(format!("Failed to register PromptCard: {}", e)))?;

        debug!(
            "Registered PromptCard: {}/{} version {} (uid: {})",
            prompt_card.space, prompt_card.name, prompt_card.version, prompt_card.uid
        );
    }

    *card = CardVariant::Card(Card {
        alias: card_path_variant.alias.clone(),
        registry_type: card_path_variant.registry_type.clone(),
        space: prompt_card.space.clone(),
        name: prompt_card.name.clone(),
        version: Some(prompt_card.version.clone()),
        uid: Some(prompt_card.uid.clone()),
        drift: card_path_variant.drift.clone(),
        version_type: card_path_variant.version_type.clone(),
    });

    Ok(())
}

fn extract_and_validate_cards(spec: &OpsmlServiceSpec) -> Result<Vec<Card>, CliError> {
    let Some(service_config) = &spec.service else {
        return Ok(Vec::new());
    };

    let Some(cards) = &service_config.cards else {
        return Ok(Vec::new());
    };

    let mut validated_cards = Vec::with_capacity(cards.len());

    for card in cards {
        match card {
            CardVariant::Card(c) => validated_cards.push(c.clone()),
            CardVariant::Path(_) => {
                return Err(CliError::Error(
                    "Card paths must be processed before creating service card".to_string(),
                ));
            }
        }
    }

    validate_service_cards(&mut validated_cards)?;
    Ok(validated_cards)
}

/// Attempts to register a service card based on the provided spec.
/// Flow:
/// 1. Iterate through cards in spec. If any cards/prompts have paths, load them and register them first.
/// 2. Validate the cards in the spec after loading any cards from paths to ensure they are valid before registering the service card.
/// 3. Create the service card and calculate its content hash.
/// 4. Check the content hash against the registry - if it matches, skip registration to avoid creating a new version with the same content.
///    If it doesn't match, register the service card
pub fn register_service_card(
    spec: &mut OpsmlServiceSpec,
    registries: &CardRegistries,
    space: &str,
    name: &str,
) -> Result<(ServiceCard, bool), CliError> {
    process_cards(spec, registries)?;

    let registry = registries.get_registry(&RegistryType::from(&spec.service_type));
    let cards = extract_and_validate_cards(spec)?;
    let mut service = ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)?;

    if card_exists_in_registry(registry, &service)? {
        warn!(
            "ServiceCard content hash matches registry, skipping registration for: {}/{}",
            space, name
        );
        return Ok((service, false));
    }

    registry.register_card_rs(&mut service, VersionType::Minor)?;
    Ok((service, true))
}

fn process_cards(spec: &mut OpsmlServiceSpec, registries: &CardRegistries) -> Result<(), CliError> {
    let Some(service_config) = &mut spec.service else {
        return Ok(());
    };

    let Some(cards) = &mut service_config.cards else {
        return Ok(());
    };

    for card in cards.iter_mut() {
        if *card.registry_type() == RegistryType::Prompt {
            let prompt_registry = registries.get_registry(&RegistryType::Prompt);
            process_prompt_card_from_path(card, &spec.root_path, prompt_registry)?;
        }
    }

    Ok(())
}

fn card_exists_in_registry(
    registry: &CardRegistry,
    service: &ServiceCard,
) -> Result<bool, CliError> {
    registry
        .compare_card_hash(service.calculate_content_hash()?.as_slice())
        .map_err(Into::into)
}
