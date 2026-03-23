// This module contains utility functions for the opsml_cli crate.
use crate::error::CliError;
use opsml_cards::{PromptCard, ServiceCard};
pub use opsml_registry::utils::validate_service_cards;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_semver::VersionType;
use opsml_service::OpsmlServiceSpec;
use opsml_types::contracts::{Card, CardArgs};
use opsml_types::{RegistryType, contracts::CardVariant};
use std::collections::HashSet;
use std::path::Path;
use tracing::{debug, error, instrument, warn};

fn validate_alias(alias: &str) -> Result<(), CliError> {
    use std::path::Component;
    let mut components = Path::new(alias).components();
    match (components.next(), components.next()) {
        (Some(Component::Normal(_)), None) => Ok(()),
        _ => Err(CliError::Error(format!(
            "Invalid alias '{alias}': must be a single path component with no separators or traversals"
        ))),
    }
}

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

    if card_path_variant.path.is_absolute() {
        return Err(CliError::Error(format!(
            "Absolute paths are not allowed in Path variants: {:?}",
            card_path_variant.path
        )));
    }
    let joined = root_path.join(&card_path_variant.path);
    let card_path = joined
        .canonicalize()
        .map_err(|e| CliError::Error(format!("Failed to resolve path {:?}: {}", joined, e)))?;
    let root_canonical = root_path.canonicalize().map_err(|e| {
        CliError::Error(format!(
            "Failed to resolve root path {:?}: {}",
            root_path, e
        ))
    })?;
    if !card_path.starts_with(&root_canonical) {
        return Err(CliError::Error(format!(
            "Path traversal detected: {:?} escapes root {:?}",
            card_path_variant.path, root_path
        )));
    }

    debug!(
        "Loading PromptCard from path: {:?} for alias: {}",
        card_path, card_path_variant.alias
    );

    let mut prompt_card = PromptCard::from_path(card_path)
        .map_err(|e| CliError::Error(format!("Failed to load PromptCard: {}", e)))?;

    let prompt_hash = prompt_card.calculate_content_hash()?;
    if let Some(existing_card) = registry.compare_card_hash(prompt_hash.as_slice())? {
        warn!(
            "PromptCard content hash matches registry, skipping registration for: {}/{}",
            prompt_card.space, prompt_card.name
        );
        // If the card already exists in the registry, we need to get space, name, version, and uid from the registry to populate the CardVariant for downstream use in service card registration
        // update prompt_card with existing card info from registry
        prompt_card.space = existing_card.space;
        prompt_card.name = existing_card.name;
        prompt_card.version = existing_card.version;
        prompt_card.uid = existing_card.uid;
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

pub(crate) fn extract_and_validate_cards(spec: &OpsmlServiceSpec) -> Result<Vec<Card>, CliError> {
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
#[instrument(skip_all)]
pub fn register_service_card(
    spec: &mut OpsmlServiceSpec,
    registries: &CardRegistries,
    space: &str,
    name: &str,
) -> Result<(ServiceCard, bool), CliError> {
    process_cards(spec, registries)?;

    let registry = registries.get_registry(&RegistryType::from(&spec.service_type));
    let cards = extract_and_validate_cards(spec)?;

    // Create the ServiceCard from its components to calculate the content hash before registration
    // This becomes the source of truth
    let mut service = ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)?;

    if let Some(existing_card) = card_exists_in_registry(registry, &service)? {
        warn!(
            "ServiceCard content hash matches registry, skipping registration for: {}/{}",
            space, name
        );
        // update service card with existing card info from registry to ensure version and uid are populated for downstream use
        service.space = existing_card.space;
        service.name = existing_card.name;
        service.version = existing_card.version;
        service.uid = existing_card.uid;
        return Ok((service, false));
    }

    registry.register_card_rs(&mut service, VersionType::Minor)?;
    Ok((service, true))
}

#[instrument(skip_all)]
fn process_cards(spec: &mut OpsmlServiceSpec, registries: &CardRegistries) -> Result<(), CliError> {
    let Some(service_config) = &mut spec.service else {
        return Ok(());
    };

    let Some(cards) = &mut service_config.cards else {
        return Ok(());
    };

    for card in cards.iter_mut() {
        if *card.registry_type() == RegistryType::Prompt && matches!(card, CardVariant::Path(_)) {
            let prompt_registry = registries.get_registry(&RegistryType::Prompt);
            process_prompt_card_from_path(card, &spec.root_path, prompt_registry)?;
        }
    }

    Ok(())
}

#[instrument(skip_all)]
fn card_exists_in_registry(
    registry: &CardRegistry,
    service: &ServiceCard,
) -> Result<Option<CardArgs>, CliError> {
    let content_hash = service.calculate_content_hash()?;
    Ok(registry
        .compare_card_hash(content_hash.as_slice())
        .inspect_err(|e| {
            error!("Error comparing card hash with registry: {}", e);
        })?)
}

/// Creates a ServiceCard locally without registering it.
/// For each card in the spec:
///   - `CardVariant::Path`: loads the card from disk, saves it to `target_path/{alias}/`,
///     converts to `CardVariant::Card`, and tracks alias in returned set.
///   - `CardVariant::Card`: passes through as-is.
///
/// Returns the ServiceCard and the set of aliases that were loaded from local paths
/// (these don't need to be downloaded from the registry).
#[instrument(skip_all)]
pub(crate) fn create_service_card_local(
    spec: &mut OpsmlServiceSpec,
    space: &str,
    name: &str,
    target_path: &Path,
) -> Result<(ServiceCard, HashSet<String>), CliError> {
    let mut local_aliases = HashSet::new();

    // Process Path variants: load from disk and save to target_path
    if let Some(service_config) = &mut spec.service
        && let Some(cards) = &mut service_config.cards
    {
        for card in cards.iter_mut() {
            if let CardVariant::Path(card_path_variant) = card {
                if card_path_variant.path.is_absolute() {
                    return Err(CliError::Error(format!(
                        "Absolute paths are not allowed in Path variants: {:?}",
                        card_path_variant.path
                    )));
                }
                let joined = spec.root_path.join(&card_path_variant.path);
                let card_path = joined.canonicalize().map_err(|e| {
                    CliError::Error(format!("Failed to resolve path {:?}: {}", joined, e))
                })?;
                let root_canonical = spec.root_path.canonicalize().map_err(|e| {
                    CliError::Error(format!(
                        "Failed to resolve root path {:?}: {}",
                        spec.root_path, e
                    ))
                })?;
                if !card_path.starts_with(&root_canonical) {
                    return Err(CliError::Error(format!(
                        "Path traversal detected: {:?} escapes root {:?}",
                        card_path_variant.path, spec.root_path
                    )));
                }

                let alias = card_path_variant.alias.clone();
                validate_alias(&alias)?;
                let save_dir = target_path.join(&alias);

                if !save_dir.exists() {
                    std::fs::create_dir_all(&save_dir)?;
                }

                match card_path_variant.registry_type {
                    RegistryType::Prompt => {
                        debug!(
                            "Loading PromptCard from path: {:?} for alias: {}",
                            card_path, alias
                        );
                        let mut prompt_card = PromptCard::from_path(card_path).map_err(|e| {
                            CliError::Error(format!("Failed to load PromptCard: {}", e))
                        })?;

                        prompt_card.save_card(save_dir).map_err(|e| {
                            CliError::Error(format!("Failed to save PromptCard locally: {}", e))
                        })?;

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
                    }
                    _ => {
                        return Err(CliError::Error(format!(
                            "Unsupported registry type for local Path variant: {:?}",
                            card_path_variant.registry_type
                        )));
                    }
                }

                local_aliases.insert(alias);
            }
        }
    }

    let cards = extract_cards(spec)?;

    let service = ServiceCard::rust_new(space.to_string(), name.to_string(), cards, spec)
        .map_err(CliError::CreateServiceError)?;

    Ok((service, local_aliases))
}

/// Extracts Card variants from the spec without registry validation.
/// All Path variants must already be converted to Card variants before calling this.
fn extract_cards(spec: &OpsmlServiceSpec) -> Result<Vec<Card>, CliError> {
    let Some(service_config) = &spec.service else {
        return Ok(Vec::new());
    };

    let Some(cards) = &service_config.cards else {
        return Ok(Vec::new());
    };

    let mut result = Vec::with_capacity(cards.len());

    for card in cards {
        match card {
            CardVariant::Card(c) => result.push(c.clone()),
            CardVariant::Path(_) => {
                return Err(CliError::Error(
                    "Card paths must be processed before creating service card".to_string(),
                ));
            }
        }
    }

    Ok(result)
}
