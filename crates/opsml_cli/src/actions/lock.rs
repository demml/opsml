use crate::actions::utils::register_service_card;
use crate::cli::arg::DownloadCard;
use crate::download_service;
use crate::error::CliError;
use opsml_cards::ServiceCard;
use opsml_colors::Colorize;
use opsml_registry::error::RegistryError;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_service::{Card, ServiceConfig, ServiceSpec};
use opsml_toml::{LockArtifact, LockFile};
use opsml_types::IntegratedService;
use opsml_types::{
    contracts::{CardEntry, CardRecord},
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
/// As an example, modelcards can activate drift profile via a drift_config in the toml
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
                        version: current_card.version.clone(),
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
/// 1. For each card defined in the toml file, find the latest card in the registry
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
    service_cards: &[CardEntry],
    cards: &[Card],
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
                if card.uid != latest_card.uid() {
                    return Ok(true);
                }
            }
            // No existing entry found - needs refresh
            None => return Ok(true),
        }
    }

    Ok(false)
}

/// create lock entry for a service
/// # Arguments
/// * `config` - ServiceConfig
fn lock_service_card(
    config: ServiceConfig,
    space: &str,
    name: &str,
) -> Result<LockArtifact, CliError> {
    debug!("Locking service with config: {:?}", config);

    // Get app cards from service config
    let spec_cards = config.cards.as_ref().ok_or(CliError::MissingServiceCards)?;

    let registries = CardRegistries::new()?;

    // Initialize registry and get service from registry
    let service =
        get_service_from_registry(&registries.service, space, name, config.version.as_ref())?;

    // Handle service creation if it doesn't exist
    if service.is_none() {
        let service_card = register_service_card(&config, &registries.service, space, name)?;

        // Postprocess the service card if needed (e.g., activate drift profiles)
        postprocess_service_card(spec_cards, &service_card, &registries.service)?;

        return Ok(LockArtifact {
            space: service_card.space.clone(),
            name: service_card.name.clone(),
            version: service_card.version.clone(),
            uid: service_card.uid.clone(),
            registry_type: RegistryType::Service,
            write_dir: config.write_dir.unwrap_or("opsml_service".to_string()),
        });
    }
    // Process existing service (need to compare existing service cards to those defined in toml)
    let service = service.unwrap();
    // Get card UIDs from service
    let service_cards = service.cards().ok_or(CliError::MissingCardEntriesError)?;
    let needs_refresh = process_service_cards(&service_cards, spec_cards, &registries)?;

    let lock_entry = match needs_refresh {
        true => {
            // If refresh is needed, register the service again
            let service_card = register_service_card(&config, &registries.service, space, name)?;

            // Postprocess the service card if needed (e.g., activate drift profiles)
            postprocess_service_card(spec_cards, &service_card, &registries.service)?;

            LockArtifact {
                space: service_card.space.clone(),
                name: service_card.name.clone(),
                version: service_card.version.clone(),
                uid: service_card.uid.clone(),
                registry_type: RegistryType::Service,
                write_dir: config.write_dir.unwrap_or("opsml_app".to_string()),
            }
        }
        false => {
            // No refresh needed, return existing entry
            LockArtifact {
                space: service.space().to_string(),
                name: service.name().to_string(),
                version: service.version().to_string(),
                uid: service.uid().to_string(),
                registry_type: RegistryType::Service,
                write_dir: config.write_dir.unwrap_or("opsml_app".to_string()),
            }
        }
    };

    Ok(lock_entry)
}

/// Create the the lock file for the app
///fn lock_service(service: ServiceConfig) -> Result<LockArtifact, CliError> {
///    // Create a lock file for the app
///    // Only support's  service currently
///    lock_service_card(service)
///}

#[pyfunction]
#[pyo3(signature = (path, write_path=None))]
pub fn install_service(path: PathBuf, write_path: Option<PathBuf>) -> Result<(), CliError> {
    debug!("Installing service from lock file");

    println!(
        "{}",
        Colorize::green("Downloading service for opsml.lock file")
    );

    let lockfile = LockFile::read(&path)?;

    for artifact in lockfile.artifact {
        match artifact.registry_type {
            RegistryType::Service => {
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

/// Will create an `opsml.lock` file based on the service configuration specified within the opsmlspec.yml file.
#[pyfunction]
#[pyo3(signature = (path=None, filename=None))]
pub fn lock_service(path: Option<PathBuf>, filename: Option<&str>) -> Result<(), CliError> {
    debug!("Locking service with path: {:?}", path);

    let service = ServiceSpec::from_path(path.as_deref(), filename)?;

    // Create a lock file
    let lock_file = LockFile {
        artifact: vec![lock_service_card(
            service.service.clone(),
            service.space(),
            &service.name,
        )?],
    };

    lock_file.write(&service.root_path)?;

    Ok(())
}
