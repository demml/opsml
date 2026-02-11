use crate::error::RegistryError;
use crate::registries::card::OpsmlCardRegistry;
use crate::CardRegistries;
use opsml_cards::{
    traits::OpsmlCard, DataCard, ExperimentCard, ModelCard, PromptCard, ServiceCard,
};
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_storage::storage_client;
use opsml_types::contracts::*;
use opsml_types::*;
use pyo3::prelude::*;
use pyo3::types::PyString;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;
use tempfile::TempDir;
use tracing::{debug, error, instrument};

/// Helper function to load a card and convert it to PyObject
///
/// # Arguments
/// * `py`: Python interpreter
/// * `card_registries`: Card registries
/// * `card`: Card to load
/// * `interface`: Optional interface to use
/// * `load_kwargs`: Optional load kwargs
///
fn load_and_extract_card(
    py: Python,
    card_registries: &CardRegistries,
    card: &Card,
    interface: Option<&Bound<'_, PyAny>>,
) -> Result<Py<PyAny>, RegistryError> {
    let card_obj = match card.registry_type {
        RegistryType::Model => card_registries.model.load_card(
            py,
            card.uid.clone(),
            Some(card.space.clone()),
            Some(card.name.clone()),
            card.version.clone(),
            interface,
        )?,
        RegistryType::Data => card_registries.data.load_card(
            py,
            card.uid.clone(),
            Some(card.space.clone()),
            Some(card.name.clone()),
            card.version.clone(),
            interface,
        )?,
        RegistryType::Experiment => card_registries.experiment.load_card(
            py,
            card.uid.clone(),
            Some(card.space.clone()),
            Some(card.name.clone()),
            card.version.clone(),
            None,
        )?,
        RegistryType::Prompt => card_registries.prompt.load_card(
            py,
            card.uid.clone(),
            Some(card.space.clone()),
            Some(card.name.clone()),
            card.version.clone(),
            None,
        )?,
        _ => {
            return Err(RegistryError::CardTypeNotSupported(
                card.registry_type.clone(),
            ));
        }
    };

    Ok(card_obj.into_py_any(py)?)
}

pub enum CardEnum {
    ModelCard(ModelCard),
    DataCard(DataCard),
    ExperimentCard(Box<ExperimentCard>),
    PromptCard(Box<PromptCard>),
    ServiceCard(Box<ServiceCard>),
}

impl CardEnum {
    #[allow(clippy::needless_lifetimes)]
    pub fn into_bound_py_any<'py>(
        self,
        py: Python<'py>,
    ) -> Result<Bound<'py, PyAny>, RegistryError> {
        let card = match self {
            CardEnum::ModelCard(card) => card.into_bound_py_any(py),
            CardEnum::DataCard(card) => card.into_bound_py_any(py),
            CardEnum::ExperimentCard(card) => card.into_bound_py_any(py),
            CardEnum::PromptCard(card) => card.into_bound_py_any(py),
            CardEnum::ServiceCard(card) => card.into_bound_py_any(py),
        };

        Ok(card?)
    }
}

pub fn load_service_card<'py>(
    py: Python<'py>,
    service: &mut ServiceCard,
    interfaces: Option<HashMap<String, Bound<'py, PyAny>>>,
) -> Result<(), RegistryError> {
    let card_registries = CardRegistries::new().inspect_err(|e| {
        error!("Failed to create card registries: {e}");
    })?;

    for card in &service.cards {
        // Skip if already loaded
        if service.card_objs.contains_key(&card.alias) {
            debug!("Card {} already exists in card_objs", card.alias);
            continue;
        }

        // get interface for the card if exists
        let interface = interfaces.as_ref().and_then(|i| i.get(&card.alias));

        let card_obj =
            load_and_extract_card(py, &card_registries, card, interface).map_err(|e| {
                error!("Failed to load card: {e}");
                e
            })?;
        service.card_objs.insert(card.alias.clone(), card_obj);
    }

    Ok(())
}

pub fn check_if_card(card: &Bound<'_, PyAny>) -> Result<(), RegistryError> {
    let is_card: bool = card.getattr("is_card")?.extract()?;

    if is_card {
        Ok(())
    } else {
        let type_name = card
            .get_type()
            .name()
            .unwrap_or_else(|_| PyString::new(card.py(), &CommonKwargs::Undefined.to_string()));
        Err(RegistryError::InvalidCardType(type_name.to_string()))
    }
}

/// Create a card from a json string
///
/// # Arguments
/// * `py` - Python interpreter
/// * `card_json` - JSON string of the card
/// * `interface` - Optional interface for the card
/// * `key` - Artifact key
/// * `fs` - File system storage
/// * `rt` - Tokio runtime
///
/// # Returns
/// * `Bound<PyAny>` - Bound card
///
/// # Errors
/// * `RegistryError` - Error creating card
pub fn card_from_string<'py>(
    py: Python<'py>,
    card_json: String,
    interface: Option<&Bound<'py, PyAny>>,
    key: ArtifactKey,
) -> Result<CardEnum, RegistryError> {
    let card = match key.registry_type {
        RegistryType::Model => {
            let mut card =
                ModelCard::model_validate_json(py, card_json, interface).inspect_err(|e| {
                    error!("Failed to validate ModelCard: {e}");
                })?;

            card.set_artifact_key(key);
            CardEnum::ModelCard(card)
        }

        RegistryType::Data => {
            let mut card =
                DataCard::model_validate_json(py, card_json, interface).inspect_err(|e| {
                    error!("Failed to validate DataCard: {e}");
                })?;

            card.set_artifact_key(key);
            CardEnum::DataCard(card)
        }

        RegistryType::Experiment => {
            let mut card = ExperimentCard::model_validate_json(card_json).inspect_err(|e| {
                error!("Failed to validate ExperimentCard: {e}");
            })?;

            card.set_artifact_key(key);
            CardEnum::ExperimentCard(Box::new(card))
        }

        RegistryType::Prompt => {
            let card = PromptCard::model_validate_json(card_json).inspect_err(|e| {
                error!("Failed to validate PromptCard: {e}");
            })?;

            CardEnum::PromptCard(Box::new(card))
        }

        RegistryType::Service => {
            let card = ServiceCard::model_validate_json(card_json).inspect_err(|e| {
                error!("Failed to validate ServiceCard: {e}");
            })?;

            CardEnum::ServiceCard(Box::new(card))
        }

        _ => {
            return Err(RegistryError::RegistryTypeNotSupported(
                key.registry_type.clone(),
            ));
        }
    };

    Ok(card)
}

/// Download a card
///
/// # Arguments
/// * `py` - Python interpreter
/// * `key` - Artifact key
/// * `fs` - File system storage
/// * `rt` - Tokio runtime
/// * `interface` - Optional interface for the card
///
/// # Returns
/// * `Bound<PyAny>` - Bound card
///
/// # Errors
/// * `RegistryError` - Error downloading card
pub fn download_card<'py>(
    py: Python<'py>,
    key: ArtifactKey,
    interface: Option<&Bound<'py, PyAny>>,
) -> Result<Bound<'py, PyAny>, RegistryError> {
    let decryption_key = key.get_decrypt_key().inspect_err(|e| {
        error!("Failed to get decryption key: {e}");
    })?;

    let tmp_dir = TempDir::new()?;

    let tmp_path = tmp_dir.keep();
    let orig_rpath = PathBuf::from(&key.storage_key);

    let rpath = orig_rpath.join(SaveName::Card).with_extension(Suffix::Json);

    // add Card.json to tmp_path and rpath
    let lpath = tmp_path.join(SaveName::Card).with_extension(Suffix::Json);

    storage_client()?.get(&lpath, &rpath, false)?;
    decrypt_directory(&tmp_path, &decryption_key)?;

    let json_string = std::fs::read_to_string(&lpath).inspect_err(|e| {
        error!("Failed to read card json: {e}");
    })?;

    let mut card = card_from_string(py, json_string, interface, key)?;

    match &mut card {
        // load all cards in the service
        CardEnum::ServiceCard(service) => {
            debug!("Loading service card: {}", service.name);
            // need to check if interface is not None, if not None it needs to be
            // HashMap<String, Bound<PyAny>>
            let kwargs =
                interface.and_then(|i| i.extract::<HashMap<String, Bound<'py, PyAny>>>().ok());

            load_service_card(py, service, kwargs)?;
        }

        CardEnum::PromptCard(prompt_card) => {
            // Load drift profile if exists
            if let Some(_drift_profile_uri_map) = prompt_card.metadata.drift_profile_uri_map.clone()
            {
                let rpath = orig_rpath.join(SaveName::Drift);

                let lpath = tmp_path.join(SaveName::Drift);
                storage_client()?.get(&lpath, &rpath, true)?;
                decrypt_directory(&lpath, &decryption_key)?;

                prompt_card.load_drift_profile(&tmp_path).inspect_err(|e| {
                    error!("Failed to load drift profile: {e}");
                })?;
            }
        }
        _ => debug!("Card is not a service, skipping service loading"),
    }

    card.into_bound_py_any(py)
}

/// Save card artifacts to storage
/// Using a runtime, this method with
/// (1) create an artifact key to be used to encrypt data
/// (2) save the card to a temporary directory (with encryption)
/// (3) Transfer all files in the temporary directory to the storage system
///
/// # Arguments
/// * `py` - Python interpreter
/// * `card` - Card to save
/// * `save_kwargs` - Optional save kwargs
///
/// # Returns
/// * `Result<(), RegistryError>` - Result
#[instrument(skip_all)]
pub fn upload_card_artifacts(path: PathBuf, key: &ArtifactKey) -> Result<(), RegistryError> {
    // create temp path for saving
    // TODO: why is this named decrypt key?
    let encryption_key = key.get_decrypt_key()?;

    encrypt_directory(&path, &encryption_key)?;
    debug!("Encrypted card artifacts");

    storage_client()?.put(&path, &key.storage_path(), true)?;
    debug!("Saved card artifacts to storage");

    Ok(())
}

/// Helper for converting service card attributes to options
fn to_option(value: &str) -> Option<String> {
    match value == CommonKwargs::Undefined.to_string() {
        true => None,
        false => Some(value.to_string()),
    }
}

/// Validates a service card card by checking if it exists in the registry
///
/// # Process
/// 1. Check if Card exists in the registry
/// 2. If it exists, update the card metadata
/// 3. If it does not exist, return an error
///
/// # Arguments
/// * `card` - Card to validate
///
/// # Returns
/// * `Result<(), RegistryError>` - Result
///
/// # Errors
/// * `RegistryError` - Error validating card
///   Will return an error if the card does not exist in the registry
fn validate_and_update_card(card: &mut Card) -> Result<(), RegistryError> {
    let reg = OpsmlCardRegistry::new(card.registry_type.clone())?;

    let args = CardQueryArgs {
        uid: card.uid.clone(),
        space: to_option(&card.space),
        name: to_option(&card.name),
        version: card.version.clone(),
        registry_type: card.registry_type.clone(),
        sort_by_timestamp: Some(false),
        ..Default::default()
    };

    let cards = reg.list_cards(&args).inspect_err(|e| {
        error!("Failed to list cards: {e}");
    })?;

    if cards.is_empty() {
        return Err(RegistryError::CustomError(format!(
            "Card {:?}/{:?} does not exist in the {:?} registry",
            card.space, card.name, card.registry_type
        )));
    }

    // Update card metadata
    if let Some(found_card) = cards.first() {
        card.name = found_card.name().to_string();
        card.space = found_card.space().to_string();
        card.version = Some(found_card.version().to_string());
        card.uid = Some(found_card.uid().to_string());
        debug!("Updated card metadata for name: {:?}", card.name);
    } else {
        return Err(RegistryError::CustomError(format!(
            "Card {:?}/{:?} does not exist in the {:?} registry",
            card.space, card.name, card.registry_type
        )));
    }
    Ok(())
}

/// Validate a service card
/// This function will validate each card in the service
/// The registry will be queried based on the card args.
/// Returned record will be used to update card attributes as part of ServiceCard
/// If a card does not exist, it will return an error
///
/// # Arguments
/// * service - Card service to validate
///
/// # Returns
/// * `Result<(), RegistryError>` - Result
///
/// # Errors
/// * `RegistryError` - Error validating card
#[instrument(skip_all)]
pub fn validate_service_cards(service: &mut [Card]) -> Result<(), RegistryError> {
    // iterate over each card in the service
    for card in service.iter_mut() {
        validate_and_update_card(card)?;
    }
    Ok(())
}

/// Verify that the card is valid
/// If a service card is passed, verify that all cards in the service are valid
///
/// # Arguments
/// * `card` - Card to verify
/// * `registry_type` - Registry type
///
/// # Returns
/// * `Result<(), RegistryError>` - Result
///
/// # Errors
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
            let data_registry = OpsmlCardRegistry::new(RegistryType::Data)?;
            // check if datacard exists in the registry
            let exists = data_registry.check_card_uid(&datacard_uid)?;

            if !exists {
                return Err(RegistryError::DataCardNotExistError);
            }
        }
    }

    if card.is_instance_of::<ServiceCard>() {
        let mut service = card
            .getattr("cards")
            .map_err(|e| {
                error!("Failed to get cards from service: {e}");
                RegistryError::FailedToGetCardsFromService
            })?
            .extract::<Vec<Card>>()
            .map_err(|e| {
                error!("Failed to extract cards from service: {e}");
                RegistryError::FailedToExtractCardsFromService
            })?;

        validate_service_cards(&mut service)?;

        // Update the Python service card with the updated cards
        card.setattr("cards", service.into_py_any(card.py()).unwrap())
            .map_err(|e| {
                error!("Failed to update service card: {e}");
                RegistryError::UpdateServiceCardError
            })?;
    }

    let card_registry_type = card.getattr("registry_type")?.extract::<RegistryType>()?;

    // assert that the card registry type is the same as the registry type
    if card_registry_type != *registry_type {
        return Err(RegistryError::RegistryTypeMismatchError);
    }

    debug!("Verified card");

    Ok(())
}

/// Verify that the card is valid
/// This will be expanded in the future
#[instrument(skip_all)]
pub fn verify_card_rs<T>(card: &T) -> Result<(), RegistryError>
where
    T: OpsmlCard,
{
    if !card.is_card() {
        return Err(RegistryError::NotValidCardError);
    }

    debug!("Verified card");

    Ok(())
}
