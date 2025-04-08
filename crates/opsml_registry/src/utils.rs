use crate::base::OpsmlRegistry;
use opsml_cards::{DataCard, ExperimentCard, ModelCard, PromptCard};
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::error::RegistryError;
use opsml_storage::storage_client;
use opsml_types::contracts::*;
use opsml_types::*;
use pyo3::prelude::*;
use pyo3::types::PyString;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;
use tempfile::TempDir;
use tracing::{debug, error, instrument};

pub fn check_if_card(card: &Bound<'_, PyAny>) -> Result<(), RegistryError> {
    let is_card: bool = card
        .getattr("is_card")
        .map_err(|e| {
            error!("Failed to access is_card attribute: {}", e);
            RegistryError::Error("Invalid card structure".to_string())
        })?
        .extract()
        .map_err(|e| {
            error!("Failed to extract is_card value: {}", e);
            RegistryError::Error("Invalid card type".to_string())
        })?;

    if is_card {
        Ok(())
    } else {
        let type_name = card
            .get_type()
            .name()
            .unwrap_or_else(|_| PyString::new(card.py(), &CommonKwargs::Undefined.to_string()));
        Err(RegistryError::Error(format!(
            "Invalid card type: {type_name}"
        )))
    }
}

/// Create a card from a json string
///
/// # Arguments
///
/// * `py` - Python interpreter
/// * `card_json` - JSON string of the card
/// * `interface` - Optional interface for the card
/// * `key` - Artifact key
/// * `fs` - File system storage
/// * `rt` - Tokio runtime
///
/// # Returns
///
/// * `Bound<PyAny>` - Bound card
///
/// # Errors
///
/// * `RegistryError` - Error creating card
pub fn card_from_string<'py>(
    py: Python<'py>,
    card_json: String,
    interface: Option<&Bound<'py, PyAny>>,
    key: ArtifactKey,
) -> Result<Bound<'py, PyAny>, RegistryError> {
    let card = match key.registry_type {
        RegistryType::Model => {
            let mut card =
                ModelCard::model_validate_json(py, card_json, interface).map_err(|e| {
                    error!("Failed to validate ModelCard: {}", e);
                    RegistryError::Error(e.to_string())
                })?;

            card.set_artifact_key(key);
            card.into_bound_py_any(py).map_err(|e| {
                error!("Failed to convert card to bound: {}", e);
                RegistryError::Error(e.to_string())
            })?
        }

        RegistryType::Data => {
            let mut card =
                DataCard::model_validate_json(py, card_json, interface).map_err(|e| {
                    error!("Failed to validate DataCard: {}", e);
                    RegistryError::Error(e.to_string())
                })?;

            card.set_artifact_key(key);
            card.into_bound_py_any(py).map_err(|e| {
                error!("Failed to convert card to bound: {}", e);
                RegistryError::Error(e.to_string())
            })?
        }

        RegistryType::Experiment => {
            let mut card = ExperimentCard::model_validate_json(card_json).map_err(|e| {
                error!("Failed to validate ExperimentCard: {}", e);
                RegistryError::Error(e.to_string())
            })?;

            card.set_artifact_key(key);
            card.into_bound_py_any(py).map_err(|e| {
                error!("Failed to convert card to bound: {}", e);
                RegistryError::Error(e.to_string())
            })?
        }

        RegistryType::Prompt => {
            let card = PromptCard::model_validate_json(card_json).map_err(|e| {
                error!("Failed to validate PromptCard: {}", e);
                RegistryError::Error(e.to_string())
            })?;

            card.into_bound_py_any(py).map_err(|e| {
                error!("Failed to convert card to bound: {}", e);
                RegistryError::Error(e.to_string())
            })?
        }
        _ => {
            return Err(RegistryError::Error(
                "Registry type not supported".to_string(),
            ));
        }
    };

    Ok(card)
}

/// Download a card
///
/// # Arguments
///
/// * `py` - Python interpreter
/// * `key` - Artifact key
/// * `fs` - File system storage
/// * `rt` - Tokio runtime
/// * `interface` - Optional interface for the card
///
/// # Returns
///
/// * `Bound<PyAny>` - Bound card
///
/// # Errors
///
/// * `RegistryError` - Error downloading card
pub fn download_card<'py>(
    py: Python<'py>,
    key: ArtifactKey,
    interface: Option<&Bound<'py, PyAny>>,
) -> Result<Bound<'py, PyAny>, RegistryError> {
    let decryption_key = key.get_decrypt_key().map_err(|e| {
        error!("Failed to get decryption key: {}", e);
        RegistryError::Error(e.to_string())
    })?;

    let tmp_dir = TempDir::new().map_err(|e| {
        error!("Failed to create temporary directory: {}", e);
        RegistryError::Error("Failed to create temporary directory".to_string())
    })?;

    let tmp_path = tmp_dir.into_path();
    let rpath = PathBuf::from(&key.storage_key);

    let rpath = rpath.join(SaveName::Card).with_extension(Suffix::Json);

    // add Card.json to tmp_path and rpath
    let lpath = tmp_path.join(SaveName::Card).with_extension(Suffix::Json);

    storage_client()?.get(&lpath, &rpath, false)?;
    decrypt_directory(&tmp_path, &decryption_key)?;

    let json_string = std::fs::read_to_string(&lpath).map_err(|e| {
        error!("Failed to read card json: {}", e);
        RegistryError::Error("Failed to read card json".to_string())
    })?;

    let card = card_from_string(py, json_string, interface, key)?;

    Ok(card)
}

/// Save card artifacts to storage
/// Using a runtime, this method with
/// (1) create an artifact key to be used to encrypt data
/// (2) save the card to a temporary directory (with encryption)
/// (3) Transfer all files in the temporary directory to the storage system
///
/// # Arguments
///
/// * `py` - Python interpreter
/// * `card` - Card to save
/// * `save_kwargs` - Optional save kwargs
///
/// # Returns
///
/// * `Result<(), RegistryError>` - Result
#[instrument(skip_all)]
pub fn upload_card_artifacts(path: PathBuf, key: &ArtifactKey) -> Result<(), RegistryError> {
    // create temp path for saving
    let encryption_key = key
        .get_decrypt_key()
        .map_err(|e| RegistryError::Error(e.to_string()))?;

    encrypt_directory(&path, &encryption_key)?;
    storage_client()?.put(&path, &key.storage_path(), true)?;

    debug!("Saved card artifacts to storage");

    Ok(())
}

/// Verify that the card is valid
///
/// # Arguments
///
/// * `card` - Card to verify
/// * `registry_type` - Registry type
///
/// # Returns
///
/// * `Result<(), RegistryError>` - Result
///
/// # Errors
///
/// * `RegistryError` - Error verifying card
#[instrument(skip_all)]
pub fn verify_card(
    card: &Bound<'_, PyAny>,
    registry_type: &RegistryType,
) -> Result<(), RegistryError> {
    check_if_card(card)?;

    if card.is_instance_of::<ModelCard>() {
        let datacard_uid = card
            .getattr("metadata")
            .unwrap()
            .getattr("datacard_uid")
            .unwrap()
            .extract::<Option<String>>()
            .unwrap();

        if let Some(datacard_uid) = datacard_uid {
            let data_registry = OpsmlRegistry::new(RegistryType::Data)?;
            // check if datacard exists in the registry
            let exists = data_registry.check_card_uid(&datacard_uid)?;

            if !exists {
                return Err(RegistryError::Error(
                    "Datacard does not exist in the registry".to_string(),
                ));
            }
        }
    }

    let card_registry_type = card
        .getattr("registry_type")
        .map_err(|e| {
            error!("Failed to get card type: {}", e);
            RegistryError::Error("Failed to get card type".to_string())
        })?
        .extract::<RegistryType>()
        .map_err(|e| {
            error!("Failed to extract card type: {}", e);
            RegistryError::Error("Failed to extract card type".to_string())
        })?;

    // assert that the card registry type is the same as the registry type
    if card_registry_type != *registry_type {
        return Err(RegistryError::Error(
            "Card registry type does not match registry type".to_string(),
        ));
    }

    debug!("Verified card");

    Ok(())
}
