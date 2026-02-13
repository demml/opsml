use crate::actions::utils::register_service_card;
use crate::cli::arg::DownloadCard;
use crate::download_service;
use crate::error::CliError;
use opsml_cards::ServiceCard;
use opsml_colors::Colorize;
use opsml_registry::error::RegistryError;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_service::{service::DEFAULT_SERVICE_FILENAME, ServiceSpec};
use opsml_toml::{LockArtifact, LockFile};
use opsml_types::IntegratedService;
use opsml_types::{
    contracts::{Card, CardEntry, CardRecord, ServiceType},
    RegistryType,
};

use pyo3::prelude::*;
use scouter_client::{DriftType, ProfileStatusRequest};
use std::path::PathBuf;
use std::str::FromStr;
use std::vec;
use tracing::{debug, error, instrument};

/// Helper function to get cards from registry
fn get_service_from_registry(
    registry: &CardRegistry,
    space: &str,
    name: &str,
    version: Option<&String>,
) -> Result<Option<CardRecord>, CliError> {
    let cards = registry.list_cards(
        None,
        Some(space.to_string()),
        Some(name.to_string()),
        version.cloned(),
        None,
        None,
        Some(true),
        1,
    )?;
    Ok(cards.cards.first().cloned())
}

/// Helper function to get latest card from appropriate registry
///
/// # Arguments
/// * `registries` - RustRegistries
/// * `entry` - DeckCard
///
/// # Returns
/// * `Result<CardRecord, CliError>` - The latest card record
///
/// # Errors
/// * `CliError::MissingRegistryType` - If the registry type is missing
fn get_latest_card(registries: &CardRegistries, card: &Card) -> Result<CardRecord, CliError> {
    // extract registry type from entry
    let registry_type = card.registry_type.clone();

    let registry = match registry_type {
        RegistryType::Model => &registries.model,
        RegistryType::Experiment => &registries.experiment,
        RegistryType::Data => &registries.data,
        RegistryType::Prompt => &registries.prompt,
        RegistryType::Service => &registries.service,
        _ => return Err(RegistryError::RegistryTypeNotSupported(registry_type).into()),
    };

    let latest_cards = registry.list_cards(
        None,
        Some(card.space.clone()),
        Some(card.name.clone()),
        card.version.clone(),
        None,
        None,
        Some(false),
        1,
    )?;

    // return the first card in the list
    latest_cards.cards.first().cloned().ok_or({
        error!("Failed to get latest card");
        CliError::MissingCardError
    })
}

/// Helper for any postprocessing needed after service card registration
/// As an example, modelcards can activate drift profile via a drift_config in spec
#[instrument(skip_all)]
fn postprocess_service_card(
    spec_cards: &[Card],
    service: &ServiceCard,
    registry: &CardRegistry,
) -> Result<(), CliError> {
    if registry
        .registry
        .check_service_health(IntegratedService::Scouter)?
    {
        // check if scouter is enabled and running first
        spec_cards
            .iter()
            .filter_map(|card| card.drift.as_ref().map(|drift| (card, drift)))
            .try_for_each(|(card, drift_config)| -> Result<(), CliError> {
                let current_card = service.get_card(&card.alias)?;

                drift_config.drift_type.iter().try_for_each(|drift_type| {
                    let drift_type = DriftType::from_str(drift_type)?;

                    let request = ProfileStatusRequest {
                        space: current_card.space.clone(),
                        name: current_card.name.clone(),
                        // this occurs after registration, so version is guaranteed to be Some
                        version: current_card
                            .version
                            .clone()
                            .expect("card version is expected when updating drift configurations"),
                        active: drift_config.active,
                        drift_type: Some(drift_type),
                        deactivate_others: drift_config.deactivate_others,
                    };

                    registry.registry.update_drift_profile_status(&request)?;
                    debug!("Drift profile status updated for card: {:?}", request);
                    Ok(())
                })
            })?;
    }

    Ok(())
}

/// Process service card and check for version updates
/// The goal of this function is to:
/// 1. For each card in service spec, find the latest card in the registry
/// 2. Check if the already registered service has the same card
/// 3. If an existing card of same space and name is found, check if the uid is the same
/// 4. If the uid is different, return true (needs refresh)
/// 5. If the uid is the same, return false (no refresh needed)
/// 6. If no existing card is found, return true (needs refresh)
///
/// # Arguments
/// * `service_cards` - &[CardEntry] - List of cards associated with the most recent registered service
/// * `spec_cards` - &[DeckCard] - List of cards found in spec
/// * `registries` - &RustRegistries - Rust variant of Opsml registries
///
/// # Returns
/// * `Result<bool, CliError>` - True if a version refresh is needed, false otherwise
#[instrument(skip_all)]
fn process_service_cards(
    service_cards: &[CardEntry], // existing service cards
    cards: &[Card],              // cards from spec
    registries: &CardRegistries,
) -> Result<bool, CliError> {
    debug!("Processing service cards");
    for card in cards {
        // Find the latest card given the constraints provided in toml file
        let latest_card = get_latest_card(registries, card)?;

        // Find the card in the service
        // If the entry is not found - return true (need to increment version)
        // If the entry is found - check if the uid is different from latest card - if different - return true
        // Otherwise - return false
        // Find matching entry in existing service
        let current_card = service_cards
            .iter()
            .find(|service_card| service_card.alias == card.alias);

        // Check
        match current_card {
            Some(card) => {
                // Check if existing entry UID matches latest card UID
                let card_uid = card.uid.as_ref().ok_or(CliError::MissingCardEntriesError)?;
                if card_uid != latest_card.uid() {
                    return Ok(true);
                }
            }
            // No existing entry found - needs refresh
            None => return Ok(true),
        }
    }

    Ok(false)
}

/// Creates a LockArtifact from a ServiceCard
/// # Arguments
/// * `service_card` - &ServiceCard
/// * `write_dir` - &str
/// # Returns
/// * `LockArtifact`
fn create_lock_artifact_from_service_card(
    service_card: &ServiceCard,
    write_dir: &str,
) -> LockArtifact {
    LockArtifact {
        space: service_card.space.clone(),
        name: service_card.name.clone(),
        version: service_card.version.clone(),
        uid: service_card.uid.clone(),
        registry_type: RegistryType::Service,
        write_dir: write_dir.to_string(),
    }
}

/// Creates a LockArtifact from an existing service record
/// # Arguments
/// * `service` - &CardRecord
/// * `write_dir` - &str
/// # Returns
/// * `LockArtifact`
fn create_lock_artifact_from_existing_service(
    service: &CardRecord,
    write_dir: &str,
) -> LockArtifact {
    LockArtifact {
        space: service.space().to_string(),
        name: service.name().to_string(),
        version: service.version().to_string(),
        uid: service.uid().to_string(),
        registry_type: RegistryType::Service,
        write_dir: write_dir.to_string(),
    }
}

/// Gets the write directory with a fallback default
fn get_write_dir(spec: &ServiceSpec, default: &str) -> String {
    spec.service
        .as_ref()
        .and_then(|s| s.write_dir.clone())
        .clone()
        .unwrap_or_else(|| default.to_string())
}

/// Check if a refresh is needed based on the service and spec cards
/// # Arguments
/// * `service` - &CardRecord
/// * `spec_cards` - Option<&Vec<DeckCard>>
/// * `registries` - &RustRegistries
/// # Returns
/// * `Result<bool, CliError>`
fn check_for_refresh(
    service: &CardRecord,           // existing service
    spec_cards: Option<&Vec<Card>>, // cards from spec
    registries: &CardRegistries,
) -> Result<bool, CliError> {
    match spec_cards {
        None => Ok(true), // No spec cards means refresh needed
        Some(cards) => {
            let service_cards = service.cards().ok_or(CliError::MissingCardEntriesError)?;
            process_service_cards(&service_cards, cards, registries)
        }
    }
}

/// Create a new lock artifact for a service that does not yet exist in the registry
/// # Arguments
/// * `spec` - &ServiceSpec
/// * `registries` - &RustRegistries
/// * `spec_cards` - Option<&Vec<DeckCard>>
/// * `space` - &str
/// * `name` - &str
/// # Returns
/// * `Result<LockArtifact, CliError>`
fn create_new_service_lock(
    spec: &ServiceSpec,
    registry: &CardRegistry,
    spec_cards: Option<&Vec<Card>>,
    space: &str,
    name: &str,
) -> Result<LockArtifact, CliError> {
    let service_card = register_service_card(spec, registry, space, name)?;

    // Apply postprocessing if spec cards exist
    // some service types may not have cards
    if let Some(cards) = spec_cards {
        postprocess_service_card(cards, &service_card, registry)?;
    }

    Ok(create_lock_artifact_from_service_card(
        &service_card,
        &get_write_dir(spec, "opsml_service"),
    ))
}

/// Handles lock creation for an existing service
/// # Arguments
/// * `spec` - &ServiceSpec
/// * `registries` - &RustRegistries
/// * `spec_cards` - Option<&Vec<DeckCard>>
/// * `service` - CardRecord
/// # Returns
/// * `Result<LockArtifact, CliError>`
fn handle_existing_service_lock(
    spec: &ServiceSpec,
    service_registry: &CardRegistry,
    registries: &CardRegistries,
    spec_cards: Option<&Vec<Card>>, // cards from spec
    service: CardRecord,            // existing service
) -> Result<LockArtifact, CliError> {
    let needs_refresh = check_for_refresh(&service, spec_cards, registries)?;

    if needs_refresh {
        debug!("Service refresh needed, re-registering");
        let service_card =
            register_service_card(spec, service_registry, service.space(), service.name())?;

        if let Some(cards) = spec_cards {
            postprocess_service_card(cards, &service_card, service_registry)?;
        }

        Ok(create_lock_artifact_from_service_card(
            &service_card,
            &get_write_dir(spec, "opsml_service"),
        ))
    } else {
        debug!("No refresh needed, using existing service");
        Ok(create_lock_artifact_from_existing_service(
            &service,
            &get_write_dir(spec, "opsml_service"),
        ))
    }
}

/// Creates a lock entry for a service. This is the main function that handles locking logic.
/// If the service does not exist, it creates a new one. If it does exist, it checks if a refresh is needed.
/// As refresh is needed if any of the cards in the spec have a newer version than those in the existing service.
/// # Arguments
/// * `spec` - Service specification containing configuration
/// * `space` - Service space/namespace
/// * `name` - Service name
/// # Returns
/// * `Result<LockArtifact, CliError>` - Lock artifact or error
#[instrument(skip_all)]
pub fn lock_service_card(
    spec: &ServiceSpec,
    space: &str,
    name: &str,
) -> Result<LockArtifact, CliError> {
    debug!("Locking service {}/{}", space, name);

    let registries = CardRegistries::new()?;
    let spec_cards = spec.service.as_ref().and_then(|s| s.cards.as_ref());

    let reg = match spec.service_type {
        ServiceType::Api => &registries.service,
        ServiceType::Mcp => &registries.mcp,
        ServiceType::Agent => &registries.agent,
        _ => {
            return Err(CliError::UnsupportedServiceType(spec.service_type.clone()));
        }
    };

    let existing_service = get_service_from_registry(
        reg,
        space,
        name,
        spec.service.as_ref().and_then(|s| s.version.as_ref()),
    )?;

    match existing_service {
        None => {
            debug!("No existing service found, creating new service");
            create_new_service_lock(spec, reg, spec_cards, space, name)
        }
        Some(service) => {
            debug!("Existing service found, checking if refresh needed");
            handle_existing_service_lock(spec, reg, &registries, spec_cards, service)
        }
    }
}

/// Install services specified in an opsml.lock file
/// # Arguments
/// * `path` - PathBuf to the opsml.lock file
/// * `write_path` - Optional PathBuf to override write directory
/// # Returns
/// * `Result<(), CliError>`
#[pyfunction]
#[pyo3(signature = (path, write_path=None))]
pub fn install_service(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> {
    debug!("Installing service from lock file");

    println!(
        "{}",
        Colorize::green("Downloading service for opsml.lock file")
    );

    // if lockfile cannot be read, check if path/ DEFAULT_SPEC_PATH exists as a spec file.
    // If so, create a lockfile from it and proceed;
    let lockfile = match LockFile::read(&path) {
        Ok(lockfile) => lockfile,
        Err(original_error) => {
            let spec_path = path.join(DEFAULT_SERVICE_FILENAME);

            if !spec_path.exists() {
                return Err(original_error.into());
            }

            debug!(
                "Lock file not found, creating lock from spec at path: {:?}",
                spec_path
            );

            lock_service(spec_path)?;

            LockFile::read(&path)?
        }
    };

    for artifact in lockfile.artifact {
        match artifact.registry_type {
            RegistryType::Service | RegistryType::Mcp => {
                println!(
                    "Downloading ServiceCard {} to path {}",
                    Colorize::green(&format!(
                        "{}/{}/v{}",
                        &artifact.name, &artifact.space, &artifact.version
                    )),
                    Colorize::purple(&artifact.write_dir),
                );

                let write_path = if let Some(path) = write_path.as_ref() {
                    path.to_path_buf()
                } else {
                    let current_dir = std::env::current_dir()?;
                    // Store the `PathBuf` in a variable and return a reference to it
                    current_dir.as_path().to_path_buf()
                };

                let args = DownloadCard {
                    space: Some(artifact.space.clone()),
                    name: Some(artifact.name.clone()),
                    version: Some(artifact.version.clone()),
                    uid: Some(artifact.uid.clone()),
                    write_dir: write_path
                        .join(artifact.write_dir)
                        .into_os_string()
                        .into_string()
                        .map_err(|_| CliError::WritePathError)?,
                };

                download_service(&args)?;
            }
            _ => {
                return Err(RegistryError::RegistryTypeNotSupported(artifact.registry_type).into());
            }
        }
    }

    Ok(())
}

/// Will create an `opsml.lock` file based on the service configuration specified within the opsmlspec.yaml file.
#[pyfunction]
pub fn lock_service(path: PathBuf) -> Result<(), CliError> {
    debug!("Locking service with path: {:?}", path);
    // handle case of no cards
    let spec = ServiceSpec::from_path(&path)?;

    // Create a lock file
    let lock_file = LockFile {
        artifact: vec![lock_service_card(&spec, spec.space(), &spec.name)?],
    };

    lock_file.write(&spec.root_path)?;

    Ok(())
}
