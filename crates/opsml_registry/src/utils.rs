use crate::base::OpsmlRegistry;
use crate::CardRegistries;
use opsml_cards::{Card, CardDeck, DataCard, ExperimentCard, ModelCard, PromptCard};
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::{error::RegistryError, OpsmlError};
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
) -> PyResult<PyObject> {
    let card_obj = match card.registry_type {
        RegistryType::Model => card_registries.model.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            interface,
        )?,
        RegistryType::Data => card_registries.data.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            interface,
        )?,
        RegistryType::Experiment => card_registries.experiment.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            None,
        )?,
        RegistryType::Prompt => card_registries.prompt.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            None,
        )?,
        _ => {
            return Err(OpsmlError::new_err(format!(
                "Card type {} not supported",
                card.registry_type
            )))
        }
    };

    card_obj.into_py_any(py).map_err(|e| {
        error!("Failed to convert card to PyObject: {}", e);
        OpsmlError::new_err(e.to_string())
    })
}

pub enum CardEnum {
    ModelCard(ModelCard),
    DataCard(DataCard),
    ExperimentCard(ExperimentCard),
    PromptCard(PromptCard),
    CardDeck(CardDeck),
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
            CardEnum::CardDeck(card) => card.into_bound_py_any(py),
        };

        match card {
            Ok(card) => Ok(card),
            Err(e) => {
                error!("Failed to convert card to bound: {}", e);
                Err(RegistryError::Error(e.to_string()))
            }
        }
    }
}

pub fn load_card_deck<'py>(
    py: Python<'py>,
    deck: &mut CardDeck,
    interfaces: Option<HashMap<String, Bound<'py, PyAny>>>,
) -> Result<(), RegistryError> {
    let card_registries = CardRegistries::new().map_err(|e| {
        error!("Failed to create card registries: {}", e);
        RegistryError::Error(e.to_string())
    })?;

    for card in &deck.cards {
        // Skip if already loaded
        if deck.card_objs.contains_key(&card.alias) {
            debug!("Card {} already exists in card_objs", card.alias);
            continue;
        }

        // get interface for the card if exists
        let interface = interfaces.as_ref().and_then(|i| i.get(&card.alias));

        let card_obj =
            load_and_extract_card(py, &card_registries, card, interface).map_err(|e| {
                error!("Failed to load card: {}", e);
                RegistryError::Error(e.to_string())
            })?;
        deck.card_objs.insert(card.alias.clone(), card_obj);
    }

    Ok(())
}

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
                ModelCard::model_validate_json(py, card_json, interface).map_err(|e| {
                    error!("Failed to validate ModelCard: {}", e);
                    RegistryError::Error(e.to_string())
                })?;

            card.set_artifact_key(key);
            CardEnum::ModelCard(card)
        }

        RegistryType::Data => {
            let mut card =
                DataCard::model_validate_json(py, card_json, interface).map_err(|e| {
                    error!("Failed to validate DataCard: {}", e);
                    RegistryError::Error(e.to_string())
                })?;

            card.set_artifact_key(key);
            CardEnum::DataCard(card)
        }

        RegistryType::Experiment => {
            let mut card = ExperimentCard::model_validate_json(card_json).map_err(|e| {
                error!("Failed to validate ExperimentCard: {}", e);
                RegistryError::Error(e.to_string())
            })?;

            card.set_artifact_key(key);
            CardEnum::ExperimentCard(card)
        }

        RegistryType::Prompt => {
            let card = PromptCard::model_validate_json(card_json).map_err(|e| {
                error!("Failed to validate PromptCard: {}", e);
                RegistryError::Error(e.to_string())
            })?;

            CardEnum::PromptCard(card)
        }

        RegistryType::Deck => {
            let card = CardDeck::model_validate_json(card_json).map_err(|e| {
                error!("Failed to validate CardDeck: {}", e);
                RegistryError::Error(e.to_string())
            })?;

            CardEnum::CardDeck(card)
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

    let mut card = card_from_string(py, json_string, interface, key)?;

    match &mut card {
        // load all cards in the deck
        CardEnum::CardDeck(deck) => {
            debug!("Loading card deck: {}", deck.name);
            // need to check if interface is not None, if not None it needs to be
            // HashMap<String, Bound<PyAny>>
            let kwargs =
                interface.and_then(|i| i.extract::<HashMap<String, Bound<'py, PyAny>>>().ok());

            load_card_deck(py, deck, kwargs)?;
        }
        _ => debug!("Card is not a deck, skipping deck loading"),
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
    let encryption_key = key
        .get_decrypt_key()
        .map_err(|e| RegistryError::Error(e.to_string()))?;

    encrypt_directory(&path, &encryption_key)?;
    storage_client()?.put(&path, &key.storage_path(), true)?;

    debug!("Saved card artifacts to storage");

    Ok(())
}

fn validate_card_by_metadata(reg: &OpsmlRegistry, card: &mut Card) -> Result<(), RegistryError> {
    let args = CardQueryArgs {
        name: card.name.clone(),
        space: card.space.clone(),
        version: card.version.clone(),
        ..Default::default()
    };

    let cards = reg.list_cards(args).map_err(|e| {
        error!("Failed to list cards: {}", e);
        RegistryError::Error("Failed to list cards".to_string())
    })?;

    if cards.is_empty() {
        return Err(RegistryError::Error(format!(
            "Card {:?} does not exist in the registry",
            card.name
        )));
    }

    // Update card metadata
    if let Some(found_card) = cards.first() {
        card.name = Some(found_card.name().to_string());
        card.space = Some(found_card.space().to_string());
        card.version = Some(found_card.version().to_string());
        card.uid = Some(found_card.uid().to_string());
        debug!("Updated card metadata for name: {:?}", card.name);
    } else {
        return Err(RegistryError::Error(format!(
            "Card {:?} does not exist in the registry",
            card.name
        )));
    }
    Ok(())
}

/// Validates a card deck card by checking if it exists in the registry
///
/// # Process
/// 1. If the card has a UID, check if it exists in the registry
/// 2. If the card does not have a UID, check if it exists in the registry by name, space, and version
/// 3. If the card exists and a UID was provided, update the metadata (name, space, version)
/// 4. If the card does not exist, return an error
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
    let reg = OpsmlRegistry::new(card.registry_type.clone())?;

    match &card.uid {
        Some(uid) => {
            let args = CardQueryArgs {
                uid: Some(uid.clone()),
                registry_type: card.registry_type.clone(),
                ..Default::default()
            };

            let cards = reg.list_cards(args).map_err(|e| {
                error!("Failed to list cards: {}", e);
                RegistryError::Error("Failed to list cards".to_string())
            })?;

            if let Some(found_card) = cards.first() {
                // Update card metadata
                card.name = Some(found_card.name().to_string());
                card.space = Some(found_card.space().to_string());
                card.version = Some(found_card.version().to_string());
                debug!("Updated card metadata for uid: {}", uid);
                Ok(())
            } else {
                Err(RegistryError::Error(format!(
                    "Card {} does not exist in registry {}",
                    uid, card.registry_type
                )))
            }
        }
        None => validate_card_by_metadata(&reg, card),
    }
}

/// Validate a card deck
/// This function will validate each card in the deck
/// If a card has a UID, it will check if it exists in the registry
/// If a card does not have a UID, it will check if it exists in the registry by name, space, and version
/// Provided card will be updated with metadata (name, space, version)
/// If a card does not exist, it will return an error
///
/// # Arguments
/// * `deck` - Card deck to validate
///
/// # Returns
/// * `Result<(), RegistryError>` - Result
///
/// # Errors
/// * `RegistryError` - Error validating card
#[instrument(skip_all)]
pub fn validate_card_deck(deck: &mut [Card]) -> Result<(), RegistryError> {
    // iterate over each card in the deck
    for card in deck.iter_mut() {
        validate_and_update_card(card)?;
    }
    Ok(())
}

/// Verify that the card is valid
/// If a card deck is passed, verify that all cards in the deck are valid
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

    if card.is_instance_of::<CardDeck>() {
        let mut deck = card
            .getattr("cards")
            .map_err(|e| {
                error!("Failed to get cards from deck: {}", e);
                RegistryError::Error("Failed to get cards from deck".to_string())
            })?
            .extract::<Vec<Card>>()
            .map_err(|e| {
                error!("Failed to extract cards from deck: {}", e);
                RegistryError::Error("Failed to extract cards from deck".to_string())
            })?;

        validate_card_deck(&mut deck)?;

        // Update the Python card deck with the updated cards
        card.setattr("cards", deck.into_py_any(card.py()).unwrap())
            .map_err(|e| {
                error!("Failed to update card deck: {}", e);
                RegistryError::Error("Failed to update card deck".to_string())
            })?;
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
