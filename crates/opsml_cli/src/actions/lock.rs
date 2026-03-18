use crate::actions::utils::{create_service_card_local, register_service_card};
use crate::cli::arg::DownloadCard;
use crate::download_service;
use crate::error::CliError;
use opsml_cards::ServiceCard;
use opsml_colors::Colorize;
use opsml_registry::download::download_service_sub_cards;
use opsml_registry::error::RegistryError;
use opsml_registry::{CardRegistries, CardRegistry};
use opsml_service::{OpsmlServiceSpec, service::DEFAULT_SERVICE_FILENAME};
use opsml_toml::{LockArtifact, LockFile};
use opsml_types::IntegratedService;
use opsml_types::contracts::CardVariant;
use opsml_types::{RegistryType, contracts::CardRecord};
use pyo3::prelude::*;
use scouter_client::{DriftType, ProfileStatusRequest};
use std::path::{Path, PathBuf};
use std::str::FromStr;
use std::vec;
use tracing::error;
use tracing::{debug, instrument};

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

/// Helper for any postprocessing needed after service card registration
/// As an example, modelcards can activate drift profile via a drift_config in spec
#[instrument(skip_all)]
fn postprocess_service_card(
    spec_cards: &[CardVariant],
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
            .filter_map(|card| card.drift().map(|drift| (card, drift)))
            .try_for_each(|(card, drift_config)| -> Result<(), CliError> {
                let current_card = service.get_card(card.alias())?;

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

/// Creates a LockArtifact from a ServiceCard
/// # Arguments
/// * `service_card` - &ServiceCard
/// * `write_dir` - &str
/// # Returns
/// * `LockArtifact`
pub(crate) fn create_lock_artifact_from_service_card(
    service_card: &ServiceCard,
    write_dir: &str,
) -> LockArtifact {
    LockArtifact {
        space: service_card.space.clone(),
        name: service_card.name.clone(),
        version: service_card.version.clone(),
        uid: service_card.uid.clone(),
        registry_type: service_card.registry_type.clone(),
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
    service: &ServiceCard,
    write_dir: &str,
) -> LockArtifact {
    LockArtifact {
        space: service.space.clone(),
        name: service.name.clone(),
        version: service.version.clone(),
        uid: service.uid.clone(),
        registry_type: service.registry_type.clone(),
        write_dir: write_dir.to_string(),
    }
}

/// Gets the write directory with a fallback default
pub(crate) fn get_write_dir(spec: &OpsmlServiceSpec, default: &str) -> String {
    spec.service
        .as_ref()
        .and_then(|s| s.write_dir.clone())
        .clone()
        .unwrap_or_else(|| default.to_string())
}

/// Create a new lock artifact for a service that does not yet exist in the registry
/// # Arguments
/// * `spec` - &OpsmlServiceSpec
/// * `registries` - &RustRegistries
/// * `spec_cards` - Option<&Vec<DeckCard>>
/// # Returns
/// * `Result<LockArtifact, CliError>`
fn create_new_service_lock(
    spec: &mut OpsmlServiceSpec,
    registries: &CardRegistries,
    space: &str,
    name: &str,
) -> Result<LockArtifact, CliError> {
    let (service_card, _registered) = register_service_card(spec, registries, space, name)?;

    let spec_cards: Option<&Vec<CardVariant>> =
        spec.service.as_ref().and_then(|s| s.cards.as_ref());

    // Apply postprocessing if spec cards exist
    // some service types may not have cards
    if let Some(cards) = spec_cards {
        postprocess_service_card(
            cards,
            &service_card,
            registries.get_registry(&RegistryType::from(&spec.service_type)),
        )?;
    }

    Ok(create_lock_artifact_from_service_card(
        &service_card,
        &get_write_dir(spec, "opsml_service"),
    ))
}

/// Handles lock creation for an existing service
/// # Arguments
/// * `spec` - &OpsmlServiceSpec
/// * `spec_cards` - Option<&Vec<DeckCard>>
/// * `service` - CardRecord
/// # Returns
/// * `Result<LockArtifact, CliError>`
fn handle_existing_service_lock(
    spec: &mut OpsmlServiceSpec,
    registries: &CardRegistries,
    service: CardRecord, // existing service
) -> Result<LockArtifact, CliError> {
    let (service_card, registered) =
        register_service_card(spec, registries, service.space(), service.name())?;

    let spec_cards: Option<&Vec<CardVariant>> =
        spec.service.as_ref().and_then(|s| s.cards.as_ref());

    if let Some(cards) = spec_cards
        && registered
    {
        let registry = registries.get_registry(&RegistryType::from(&spec.service_type));
        postprocess_service_card(cards, &service_card, registry)?;
    };

    Ok(create_lock_artifact_from_existing_service(
        &service_card,
        &get_write_dir(spec, "opsml_service"),
    ))
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
pub fn lock_service_card(spec: &mut OpsmlServiceSpec) -> Result<LockArtifact, CliError> {
    // Extract owned values first to avoid holding references to spec

    let space = spec.space().to_string();
    let name = spec.name.to_string();
    let service_version = spec.service.as_ref().and_then(|s| s.version.as_ref());
    debug!("Locking service {}/{}", space, name);

    let registries = CardRegistries::new()?;

    let existing_service = get_service_from_registry(
        registries.get_registry(&RegistryType::from(&spec.service_type)),
        &space,
        &name,
        service_version,
    )?;

    match existing_service {
        None => {
            debug!("No existing service found, creating new service");
            create_new_service_lock(spec, &registries, &space, &name)
        }
        Some(service) => {
            debug!("Existing service found, checking if refresh needed");
            handle_existing_service_lock(spec, &registries, service)
        }
    }
}

fn create_lock_from_spec(path: &Path) -> Result<LockFile, CliError> {
    let spec_path = path.join(DEFAULT_SERVICE_FILENAME);

    if !spec_path.exists() {
        return Err(CliError::SpecNotFound(spec_path));
    }

    debug!(
        "Lock file not found, creating lock from spec at path: {:?}",
        spec_path
    );

    lock_service(spec_path)?;

    Ok(LockFile::read(path)?)
}

fn download_service_artifacts(
    lockfile: LockFile,
    write_path: Option<PathBuf>,
) -> Result<(), CliError> {
    for artifact in lockfile.artifact {
        match artifact.registry_type {
            RegistryType::Service | RegistryType::Mcp | RegistryType::Agent => {
                println!(
                    "Downloading ServiceCard {}, type: {} to path {}",
                    Colorize::green(&format!(
                        "{}/{}/v{}",
                        &artifact.name, &artifact.space, &artifact.version
                    )),
                    Colorize::alert(&format!("{:?}", &artifact.registry_type)),
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
                    space: Some(artifact.space),
                    name: Some(artifact.name),
                    version: Some(artifact.version),
                    uid: Some(artifact.uid),
                    write_dir: write_path
                        .join(artifact.write_dir)
                        .into_os_string()
                        .into_string()
                        .map_err(|_| CliError::WritePathError)?,
                };

                download_service(&args, artifact.registry_type)?;
            }
            _ => {
                return Err(RegistryError::RegistryTypeNotSupported(artifact.registry_type).into());
            }
        }
    }
    Ok(())
}

/// Install services specified in an opsmlspec.yaml file.
/// This is primarily used in Opsml AppState to create and load a service from a spec
/// # Arguments
/// * `path` - PathBuf to the opsmlspec.yaml file. The function will look for opsmlspec.yaml in the provided path
/// * `write_path` - Optional PathBuf to override write directory
/// # Returns
/// * `Result<(), CliError>`
pub fn install_service_from_spec(
    path: PathBuf,
    write_path: Option<PathBuf>,
) -> Result<(), CliError> {
    debug!("Installing service from spec");

    println!("{}", Colorize::green("Installing service from spec"));

    let lockfile = create_lock_from_spec(&path)?;
    download_service_artifacts(lockfile, write_path)?;
    Ok(())
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

    println!("{}", Colorize::green("Installing service"));

    // if lockfile cannot be read, check if path/ DEFAULT_SPEC_PATH exists as a spec file.
    // If so, create a lockfile from it and proceed;
    let lockfile = match LockFile::read(&path) {
        Ok(lockfile) => lockfile,
        Err(_) => create_lock_from_spec(&path)?,
    };

    download_service_artifacts(lockfile, write_path)?;
    Ok(())
}

/// Install a service locally without registering a ServiceCard.
/// Creates the ServiceCard from the spec, saves it to disk, downloads sub-card
/// artifacts from the registry (for Card variants), and writes a lock file.
/// Path variant cards are loaded from disk and saved locally instead.
///
/// # Arguments
/// * `path` - Path to the directory containing opsmlspec.yaml
/// * `write_path` - Optional override for the base write directory
pub fn install_service_locally(
    path: PathBuf,
    write_path: Option<PathBuf>,
) -> Result<(), CliError> {
    debug!("Installing service locally (no registration)");
    println!(
        "{}",
        Colorize::green("Installing service locally (no registration)")
    );

    let spec_path = path.join(DEFAULT_SERVICE_FILENAME);
    if !spec_path.exists() {
        return Err(CliError::SpecNotFound(spec_path));
    }

    let mut spec = OpsmlServiceSpec::from_path(&spec_path).inspect_err(|e| {
        error!("Failed to read service spec: {:?}", e);
    })?;

    let space = spec.space().to_string();
    let name = spec.name.to_string();
    let write_dir = get_write_dir(&spec, "opsml_service");

    let base_path = write_path.unwrap_or(path.clone());
    let target_path = base_path.join(&write_dir);

    if !target_path.exists() {
        std::fs::create_dir_all(&target_path)?;
    }

    // Create ServiceCard locally (no registration)
    let (service, local_aliases) =
        create_service_card_local(&mut spec, &space, &name, &target_path)?;

    // Save the ServiceCard to disk
    service
        .save_card(target_path.clone())
        .map_err(|e| CliError::Error(format!("Failed to save ServiceCard: {}", e)))?;

    // Download sub-cards from registry, skipping locally-saved Path variant cards
    download_service_sub_cards(&service, &target_path, &local_aliases)?;

    // Write lock file
    let lock_artifact = create_lock_artifact_from_service_card(&service, &write_dir);
    let lock_file = LockFile {
        artifact: vec![lock_artifact],
    };
    lock_file.write(&path)?;

    Ok(())
}

/// Will create an `opsml.lock` file based on the service configuration specified within the opsmlspec.yaml file.
#[pyfunction]
pub fn lock_service(path: PathBuf) -> Result<(), CliError> {
    debug!("Locking service with path: {:?}", path);
    // handle case of no cards
    let mut spec = OpsmlServiceSpec::from_path(&path).inspect_err(|e| {
        error!("Failed to read service spec: {:?}", e);
    })?;

    // Create a lock file
    let lock_file = LockFile {
        artifact: vec![lock_service_card(&mut spec).inspect_err(|e| {
            error!("Failed to lock service card: {:?}", e);
        })?],
    };
    // TODO
    lock_file.write(&spec.root_path)?;

    Ok(())
}
