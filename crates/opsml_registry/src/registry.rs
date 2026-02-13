use crate::error::RegistryError;
use crate::registries::card::OpsmlCardRegistry;
use crate::utils::verify_card_rs;
use crate::utils::{check_if_card, download_card, upload_card_artifacts, verify_card};
use crate::utils::{upload_drift_profile_map, upload_profile};
use const_format::concatcp;
use opsml_cards::traits::OpsmlCard;
use opsml_colors::Colorize;
use opsml_interfaces::DriftArgs;
use opsml_semver::VersionType;
use opsml_types::*;
use opsml_types::{cards::CardTable, contracts::*};
use opsml_utils::{clean_string, unwrap_pystring};
use pyo3::prelude::*;
use scouter_client::SCOUTER_TAG_PREFIX;
use scouter_client::try_set_span_attribute;
use std::path::PathBuf;
use tempfile::TempDir;
use tracing::{debug, error, instrument};

const MODEL_KEY_ATTR: &str = "card.model.uid";
const PROMPT_KEY_ATTR: &str = "card.prompt.uid";
const SERVICE_KEY_ATTR: &str = "card.service.uid";
const EXPERIMENT_KEY_ATTR: &str = "card.experiment.uid";
const DATA_KEY_ATTR: &str = "card.data.uid";

// combined patterns
const DATA_TAG: &str = concatcp!(SCOUTER_TAG_PREFIX, ".", DATA_KEY_ATTR);
const EXPERIMENT_TAG: &str = concatcp!(SCOUTER_TAG_PREFIX, ".", EXPERIMENT_KEY_ATTR);
const SERVICE_TAG: &str = concatcp!(SCOUTER_TAG_PREFIX, ".", SERVICE_KEY_ATTR);
const PROMPT_TAG: &str = concatcp!(SCOUTER_TAG_PREFIX, ".", PROMPT_KEY_ATTR);
const MODEL_TAG: &str = concatcp!(SCOUTER_TAG_PREFIX, ".", MODEL_KEY_ATTR);

/// Set uid as a tag on the current active span
fn set_attribute_by_registry_type(
    py: Python<'_>,
    registry_type: &RegistryType,
    uid: &str,
) -> Result<(), RegistryError> {
    let key = match registry_type {
        RegistryType::Model => MODEL_TAG,
        RegistryType::Prompt => PROMPT_TAG,
        RegistryType::Service => SERVICE_TAG,
        RegistryType::Experiment => EXPERIMENT_TAG,
        RegistryType::Data => DATA_TAG,
        _ => return Ok(()),
    };

    try_set_span_attribute(py, key, uid)?;
    Ok(())
}

/// Helper struct to hold parameters for card registration
#[derive(Debug)]
struct CardRegistrationParams<'py> {
    card: &'py Bound<'py, PyAny>,
    registry: &'py OpsmlCardRegistry,
    version_type: VersionType,
    pre_tag: Option<String>,
    build_tag: Option<String>,
    save_kwargs: Option<&'py Bound<'py, PyAny>>,
    registry_type: &'py RegistryType,
}

/// Extract registry type from a PyAny object
///
/// # Arguments
/// * `registry_type` - PyAny object
///
/// # Returns
/// * `Result<RegistryType, OpsmlError>` - Result
///
/// # Errors
/// * `OpsmlError` - Error
fn extract_registry_type(registry_type: &Bound<'_, PyAny>) -> Result<RegistryType, RegistryError> {
    match registry_type.is_instance_of::<RegistryType>() {
        true => Ok(registry_type.extract::<RegistryType>().inspect_err(|e| {
            error!("Failed to extract registry type: {e}");
        })?),
        false => {
            let registry_type = registry_type.extract::<String>().unwrap();
            Ok(RegistryType::from_string(&registry_type).inspect_err(|e| {
                error!("Failed to convert string to registry type: {e}");
            })?)
        }
    }
}

pub struct CardArgs {
    pub uid: String,
    pub name: String,
    pub space: String,
    pub version: String,
    pub registry_type: RegistryType,
}

#[pyclass]
#[pyo3(module = "opsml.card")]
#[derive(Clone)]
pub struct CardRegistry {
    registry_type: RegistryType,
    table_name: String,
    pub registry: OpsmlCardRegistry,
}

#[pymethods]
impl CardRegistry {
    /// Create new CardRegistry
    /// CardRegistries is a primary interface that provides access to the inner workings of the
    /// opsml registry system. The new method allows user to instantiate the registries from python
    /// using the __init__ method. Given that the registry is instantiated in python and some of the
    /// inner workings require an async runtime, the new method will create a new tokio runtime into an Arc so that
    /// it can be shared, cloned and used across different methods in order to prevent deadlocks.
    /// It is also cloned and passed to Cards for loading artifacts
    #[new]
    #[instrument(skip_all)]
    pub fn new(registry_type: &Bound<'_, PyAny>) -> Result<Self, RegistryError> {
        debug!("Creating new registry client");

        // check if registry_type is a valid RegistryType or String
        let registry_type = extract_registry_type(registry_type)?;

        // Create a new tokio runtime for the registry (needed for async calls)
        let registry = OpsmlCardRegistry::new(registry_type.clone())?;

        Ok(Self {
            registry_type: registry_type.clone(),
            table_name: CardTable::from_registry_type(&registry_type).to_string(),
            registry,
        })
    }

    #[getter]
    pub fn registry_type(&self) -> RegistryType {
        self.registry_type.clone()
    }

    #[getter]
    pub fn table_name(&self) -> &str {
        &self.table_name
    }

    #[getter]
    pub fn mode(&self) -> RegistryMode {
        self.registry.mode()
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (
        uid=None,
        space=None,
        name=None,
        version=None,
        max_date=None,
        tags=None,
        sort_by_timestamp=None,
        limit=100
    ))]
    #[instrument(skip_all)]
    pub fn list_cards(
        &self,
        uid: Option<String>,
        space: Option<String>,
        name: Option<String>,
        version: Option<String>,
        max_date: Option<String>,
        tags: Option<Vec<String>>,
        sort_by_timestamp: Option<bool>,
        limit: i32,
    ) -> Result<CardList, RegistryError> {
        debug!(
            "Listing cards - {:?} - {:?} - {:?} - {:?} - {:?} - {:?} - {:?} - {:?}",
            uid, name, space, version, max_date, tags, limit, sort_by_timestamp
        );

        let name = name.map(|name| clean_string(&name)).transpose()?;

        let space = space.map(|space| clean_string(&space)).transpose()?;

        let query_args = CardQueryArgs {
            uid,
            name,
            space,
            version,
            max_date,
            tags,
            limit: Some(limit),
            sort_by_timestamp,
            registry_type: self.registry_type.clone(),
        };

        let cards = self.registry.list_cards(&query_args)?;

        Ok(CardList { cards })
    }

    #[pyo3(signature = (card, version_type=VersionType::Minor, pre_tag=None, build_tag=None, save_kwargs=None))]
    #[instrument(skip_all)]
    pub fn register_card(
        &self,
        card: &Bound<'_, PyAny>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
    ) -> Result<(), RegistryError> {
        debug!("Registering card");

        let params = CardRegistrationParams {
            card,
            registry: &self.registry,
            version_type,
            pre_tag,
            build_tag,
            save_kwargs,
            registry_type: &self.registry_type,
        };

        // Wrap all operations in a single block_on to handle async operations
        Self::verify_and_register_card(card.py(), params)
    }

    #[pyo3(signature = (uid=None, space=None, name=None, version=None, interface=None))]
    #[instrument(skip_all)]
    pub fn load_card<'py>(
        &self,
        py: Python<'py>,
        uid: Option<String>,
        space: Option<String>,
        name: Option<String>,
        version: Option<String>,
        interface: Option<&Bound<'py, PyAny>>,
    ) -> Result<Bound<'py, PyAny>, RegistryError> {
        debug!(
            "Loading card - {:?} - {:?} - {:?} - {:?} - {:?}",
            uid, name, space, version, interface
        );

        // if uid, name, space, version is None, return error
        if uid.is_none() && name.is_none() && space.is_none() && version.is_none() {
            return Err(RegistryError::MissingArgsError);
        }

        // Wrap all operations in a single block_on to handle async operations
        let key = self.registry.get_key(&CardQueryArgs {
            uid,
            name,
            space,
            version,
            registry_type: self.registry_type.clone(),
            ..Default::default()
        })?;

        let card = download_card(py, key, interface)?;

        //

        Ok(card)
    }

    #[pyo3(signature = (card))]
    #[instrument(skip_all)]
    pub fn delete_card(&mut self, card: &Bound<'_, PyAny>) -> Result<(), RegistryError> {
        debug!("Deleting card");

        check_if_card(card)?;

        Self::_delete_card(&mut self.registry, card, &self.registry_type)
    }

    #[pyo3(signature = (card))]
    #[instrument(skip_all)]
    pub fn update_card(&mut self, card: &Bound<'_, PyAny>) -> Result<(), RegistryError> {
        debug!("Updating card");
        check_if_card(card)?;
        let key = Self::_update_card(&mut self.registry, card, &self.registry_type)?;

        let tmp_path = Self::save_card(card, &self.registry_type)?;

        upload_card_artifacts(tmp_path, &key)?;

        Ok(())
    }
}

impl CardRegistry {
    /// Rolls back card registration if card update or save fails
    /// This will delete the card from the registry and remove any existing artifacts
    ///
    /// # Arguments
    ///
    /// * `registry` - OpsmlCardRegistry
    /// * `card` - CreateCardResponse
    ///
    fn rollback_card(
        registry: &OpsmlCardRegistry,
        card: &CreateCardResponse,
    ) -> Result<(), RegistryError> {
        let request = DeleteCardRequest {
            uid: card.key.uid.clone(),
            space: card.space.clone(),
            registry_type: card.key.registry_type.clone(),
        };

        error!(
            "Rolling back card - {} - {}/{} - v{}",
            card.key.uid, card.space, card.name, card.version
        );
        registry.delete_card(request)?;

        Ok(())
    }

    #[instrument(skip_all)]
    fn verify_and_register_card(
        py: Python<'_>,
        params: CardRegistrationParams,
    ) -> Result<(), RegistryError> {
        // Verify card for registration
        debug!("Verifying card");
        verify_card(params.card, params.registry_type)?;

        // Register card
        debug!("Registering card");
        let create_response = Self::_register_card(
            params.registry,
            params.card,
            params.registry_type,
            params.version_type,
            params.pre_tag,
            params.build_tag,
        )
        .inspect_err(|e| error!("Failed to register card: {:?}", e))?;

        // Update card attributes
        if let Err(e) = Self::update_card_and_save(
            params.registry,
            params.card,
            &create_response,
            params.save_kwargs,
            params.registry_type,
        ) {
            Self::rollback_card(params.registry, &create_response)?;

            // raise error
            return Err(e);
        }

        set_attribute_by_registry_type(py, params.registry_type, &create_response.key.uid)?;

        println!(
            "{} - {} - {}/{} - v{}",
            Colorize::green("Registered card"),
            Colorize::purple(&params.registry_type.to_string()),
            create_response.space,
            create_response.name,
            create_response.version
        );

        Ok(())
    }

    /// Update card with server response and save artifacts
    /// If any method fails, it will return an error, which will then be used to rollback the card
    /// and delete the artifacts
    ///
    /// # Arguments
    ///
    /// * `card` - Card to update
    /// * `response` - CreateCardResponse
    /// * `save_kwargs` - Optional save kwargs
    /// * `registry_type` - RegistryType
    ///
    fn update_card_and_save(
        registry: &OpsmlCardRegistry,
        card: &Bound<'_, PyAny>,
        response: &CreateCardResponse,
        save_kwargs: Option<&Bound<'_, PyAny>>,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        // Update card attributes
        debug!("Updating card with server response");
        Self::update_card_with_server_response(response, card)
            .inspect_err(|e| error!("Failed to updated card with server response {e}"))?;

        // Helper function for handling integrations with other services
        // For example, Opsml will allow a user to register and store a Scouter drift profile
        // with a modelcard. However, this drift profile still needs to be registered with Scouter
        // so we can preform model monitoring and drift detection
        // This method also needs to be called before saving the card artifacts because Scouter will
        // set the drift profile uid on the modelcard
        debug!("Uploading integration artifacts");
        Self::upload_integration_artifacts(registry, registry_type, card, save_kwargs)?;

        // Save card artifacts to temp path
        debug!("Saving card artifacts");
        let tmp_path = Self::save_card_artifacts(card, save_kwargs, registry_type)?;

        // Save artifacts
        debug!("Uploading card artifacts");
        upload_card_artifacts(tmp_path, &response.key)?;

        Ok(())
    }

    /// Update card with server response.
    /// These are attributes that are overwritten and set by the server
    ///
    /// # Arguments
    ///
    /// * `response` - CreateCardResponse
    /// * `card` - Card to update
    ///
    /// # Returns
    ///
    /// * `Result<(), RegistryError>` - Result
    #[instrument(skip_all)]
    fn update_card_with_server_response(
        response: &CreateCardResponse,
        card: &Bound<'_, PyAny>,
    ) -> Result<(), RegistryError> {
        // update uid
        card.setattr("uid", response.key.uid.clone()).map_err(|e| {
            error!("Failed to set uid: {e}");
            RegistryError::FailedToSetAttributeError("uid")
        })?;

        // update version
        card.setattr("version", response.version.clone())
            .map_err(|e| {
                error!("Failed to set version: {e}");
                RegistryError::FailedToSetAttributeError("version")
            })?;

        // update created_at
        card.setattr("created_at", response.created_at)
            .map_err(|e| {
                error!("Failed to set created_at: {e}");
                RegistryError::FailedToSetAttributeError("created_at")
            })?;

        // update app_env
        card.setattr("app_env", response.app_env.clone())
            .map_err(|e| {
                error!("Failed to set app_env: {e}");
                RegistryError::FailedToSetAttributeError("app_env")
            })?;

        Ok(())
    }

    /// Save card artifacts to storage
    /// Using a runtime, this method will:
    /// (1) create an artifact key to be used to encrypt data
    /// (2) save the card to a temporary directory (with encryption)
    /// (3) Transfer all files in the temporary directory to the storage system
    /// # Arguments
    /// * `py` - Python interpreter
    /// * `card` - Card to save
    /// * `save_kwargs` - Optional save kwargs
    ///
    /// # Returns
    ///
    /// * `Result<(), RegistryError>` - Result
    #[instrument(skip_all)]
    fn save_card_artifacts(
        card: &Bound<'_, PyAny>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
        registry_type: &RegistryType,
    ) -> Result<PathBuf, RegistryError> {
        let tmp_dir = TempDir::new()?;

        let tmp_path = tmp_dir.keep();

        match registry_type {
            RegistryType::Experiment | RegistryType::Prompt | RegistryType::Service => {
                card.call_method1("save", (tmp_path.to_path_buf(),))
                    .inspect_err(|e| {
                        error!("Failed to save card: {e}");
                    })?;
            }

            _ => {
                // save model card artifacts
                card.call_method1("save", (tmp_path.to_path_buf(), save_kwargs))
                    .inspect_err(|e| {
                        error!("Failed to save card: {e}");
                    })?;
            }
        }

        Ok(tmp_path)
    }

    /// General method used to upload artifacts to independent services depending on registry type
    /// For example, if registering a modelcard with a drift profile, we will need to register and upload
    /// the drift profile to the scouter service
    #[instrument(skip_all)]
    fn upload_integration_artifacts(
        registry: &OpsmlCardRegistry,
        registry_type: &RegistryType,
        card: &Bound<'_, PyAny>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
    ) -> Result<(), RegistryError> {
        // If our integration types expand to other services and registry types, consider using a match statement
        if registry_type == &RegistryType::Model || registry_type == &RegistryType::Prompt {
            // ensure scouter integration is enabled before uploading artifacts
            debug!("Checking if Scouter service is enabled for integration");
            if registry.check_service_health(IntegratedService::Scouter)? {
                let drift_args = save_kwargs
                    .and_then(|kwargs| kwargs.getattr("drift").ok())
                    .and_then(|args| args.extract::<DriftArgs>().ok());

                Self::upload_scouter_artifacts(registry, card, drift_args, registry_type)?;
            }
        }
        Ok(())
    }

    /// This method will upload the scouter drift profile(s) to the registry
    /// This is done by:
    /// (1) Extracting the drift profile from the card (DriftProfileMap)
    /// (2) Extracting the values as a PyList if drift profiles
    /// (3) For each profile in list, create a profile request
    /// (4) Upload the profile to the registry
    /// (5) If drift_args is Some, update the drift profile status (allows users to immediately activate a drift profile)
    ///
    /// # Arguments
    /// * `registry` - OpsmlCardRegistry
    /// * `card` - Card to upload (ModelCard)
    /// * `drift_args` - DriftArgs
    /// * `response` - CreateCardResponse
    ///
    /// # Returns
    /// * `Result<(), RegistryError>` - Result
    #[instrument(skip_all)]
    fn upload_scouter_artifacts(
        registry: &OpsmlCardRegistry,
        card: &Bound<'_, PyAny>,
        drift_args: Option<DriftArgs>,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        // update drift config args before uploading profiles to scouter and saving
        card.call_method0("_update_drift_config_args")?;

        match registry_type {
            RegistryType::Model => {
                let profile = card.getattr("drift_profile")?;
                if !profile.is_none() {
                    upload_drift_profile_map(&profile, drift_args, registry)?
                }
            }
            RegistryType::Prompt => {
                let profile = card.getattr("eval_profile")?;
                if !profile.is_none() {
                    let uid = upload_profile(&profile, drift_args, registry)?;
                    card.call_method1("_update_eval_uid", (uid,))
                        .inspect_err(|e| {
                            error!("Failed to set eval profile uid: {e}");
                        })?;
                }
            }
            _ => {
                return Err(RegistryError::InvalidRegistryType(
                    "Expected Model or Prompt registry type".to_string(),
                ));
            }
        };

        Ok(())
    }

    /// Save card to storage
    /// Using a runtime, this method will:
    /// (1) save the card to a temporary directory (with encryption)
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `card` - Card to save
    ///
    /// # Returns
    ///
    /// * `Result<(), RegistryError>` - Result
    #[instrument(skip_all)]
    fn save_card(
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<PathBuf, RegistryError> {
        let tmp_dir = TempDir::new()?;

        let tmp_path = tmp_dir.keep();

        match registry_type {
            RegistryType::Experiment | RegistryType::Service => {
                card.call_method1("save", (tmp_path.to_path_buf(),))
                    .inspect_err(|e| {
                        error!("Failed to save card: {e}");
                    })?;
            }
            _ => {
                card.call_method1("save_card", (tmp_path.to_path_buf(),))
                    .inspect_err(|e| {
                        error!("Failed to save card: {e}");
                    })?;
            }
        }

        Ok(tmp_path)
    }

    /// Register a card in the registry
    /// Will extract RegistryCard from CardEnum and call the registry to create the card
    ///
    /// # Arguments
    ///
    /// * `card` - Card to register
    ///
    /// # Returns
    ///
    /// * `Result<(), RegistryError>` - Result
    #[instrument(skip_all)]
    fn _register_card(
        registry: &OpsmlCardRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        let registry_card = card
            .call_method0("get_registry_card")
            .inspect_err(|e| {
                error!("Failed to get registry card: {e}");
            })?
            .extract::<CardRecord>()
            .inspect_err(|e| {
                error!("Failed to extract registry card: {e}");
            })?;

        let version = unwrap_pystring(card, "version")?;

        // get version
        let version: Option<String> = if version == CommonKwargs::BaseVersion.to_string() {
            None
        } else {
            Some(version.clone())
        };

        let response = registry
            .create_card(registry_card, version, version_type, pre_tag, build_tag)
            .inspect_err(|e| {
                error!("Failed to create card in registry: {e}");
            })?;

        debug!(
            "Successfully registered card with server - {} - {}/{} - v{}",
            registry_type, response.space, response.name, response.version
        );

        Ok(response)
    }

    #[instrument(skip_all)]
    fn _delete_card(
        registry: &mut OpsmlCardRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        let uid = unwrap_pystring(card, "uid")?;
        let space = unwrap_pystring(card, "space")?;

        let delete_request = DeleteCardRequest {
            uid,
            space,
            registry_type: registry_type.clone(),
        };

        registry.delete_card(delete_request)?;

        println!("{}", Colorize::green("Deleted card"));
        debug!("Successfully deleted card");

        Ok(())
    }

    #[instrument(skip_all)]
    fn _update_card(
        registry: &mut OpsmlCardRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        let registry_card = card
            .call_method0("get_registry_card")?
            .extract::<CardRecord>()?;

        // update card
        registry.update_card(&registry_card)?;

        // get key to re-save Card.json
        let uid = registry_card.uid().to_string();
        let key = registry
            .get_key(&CardQueryArgs {
                uid: Some(uid),
                registry_type: registry_type.clone(),
                ..Default::default()
            })
            .inspect_err(|e| {
                error!("Failed to load card: {e}");
            })?;

        println!(
            "{} - {} - {}/{} - v{}",
            Colorize::green("Updated card"),
            Colorize::purple(&registry_type.to_string()),
            registry_card.space(),
            registry_card.name(),
            registry_card.version()
        );
        debug!("Successfully updated card");

        Ok(key)
    }
}

/// implementation for rust-based functionality
/// This is done because CardRegistry is intertwined with python meaning a python runtime is needed
/// There are some areas where we can register cards via rust (CLI) and so we do not need to interact with python, nor return python errors
impl CardRegistry {
    pub fn rust_new(registry_type: &RegistryType) -> Result<Self, RegistryError> {
        let registry = OpsmlCardRegistry::new(registry_type.clone())?;
        Ok(Self {
            registry_type: registry_type.clone(),
            table_name: CardTable::from_registry_type(registry_type).to_string(),
            registry,
        })
    }

    #[instrument(skip_all)]
    pub fn register_card_rs<T>(
        &self,
        card: &mut T,
        version_type: VersionType,
    ) -> Result<(), RegistryError>
    where
        T: OpsmlCard,
    {
        // Verify card for registration
        debug!("Verifying card");
        verify_card_rs(card)?;

        // Register card
        debug!("Registering card");
        let create_response = self._register_card_rs(card, version_type)?;

        // Update card attributes
        debug!("Updating card with server response");
        Self::update_card_with_server_response_rs(&create_response, card)?;

        // Save card artifacts to temp path
        debug!("Saving card artifacts");
        let tmp_path = Self::save_card_artifacts_rs(card)?;

        // Save artifacts
        debug!("Uploading card artifacts");
        upload_card_artifacts(tmp_path, &create_response.key)?;

        debug!("Successfully registered card");
        Ok(())
    }

    #[instrument(skip_all)]
    fn save_card_artifacts_rs<T>(card: &T) -> Result<PathBuf, RegistryError>
    where
        T: OpsmlCard,
    {
        let tmp_dir = TempDir::new()?;
        let tmp_path = tmp_dir.keep();
        card.save(tmp_path.clone())?;
        Ok(tmp_path)
    }

    #[instrument(skip_all)]
    fn update_card_with_server_response_rs<T>(
        response: &CreateCardResponse,
        card: &mut T,
    ) -> Result<(), RegistryError>
    where
        T: OpsmlCard,
    {
        card.set_uid(response.key.uid.clone());
        card.set_version(response.version.clone());
        card.set_created_at(response.created_at);
        card.set_app_env(response.app_env.clone());
        Ok(())
    }

    /// Rust version of _register card
    fn _register_card_rs<T>(
        &self,
        card: &T,
        version_type: VersionType,
    ) -> Result<CreateCardResponse, RegistryError>
    where
        T: OpsmlCard,
    {
        let registry_card = card.get_registry_card()?;
        let version = card.get_version();

        // get version
        let version: Option<String> = if version == CommonKwargs::BaseVersion.to_string() {
            None
        } else {
            Some(version.clone())
        };

        let response =
            self.registry
                .create_card(registry_card, version, version_type, None, None)?;

        println!(
            "{} - {} - {}/{} - v{}",
            Colorize::green("Registered card"),
            Colorize::purple(&self.registry_type().to_string()),
            response.space,
            response.name,
            response.version
        );

        debug!(
            "Successfully registered card - {} - {}/{} - v{}",
            self.registry_type(),
            response.space,
            response.name,
            response.version
        );

        Ok(response)
    }

    pub fn compare_card_hash(&self, content_hash: &[u8]) -> Result<bool, RegistryError> {
        self.registry.compare_card_hash(content_hash)
    }
}

#[pyclass]
#[pyo3(module = "opsml.card")]
#[derive(Clone)]
pub struct CardRegistries {
    #[pyo3(get)]
    pub experiment: CardRegistry,

    #[pyo3(get)]
    pub model: CardRegistry,

    #[pyo3(get)]
    pub data: CardRegistry,

    #[pyo3(get)]
    pub prompt: CardRegistry,

    #[pyo3(get)]
    pub service: CardRegistry,

    #[pyo3(get)]
    pub mcp: CardRegistry,

    #[pyo3(get)]
    pub agent: CardRegistry,
}

#[pymethods]
impl CardRegistries {
    /// Create new CardRegistries
    /// CardRegistries is a primary interface that provides access to the inner workings of the
    /// opsml registry system. The new method allows user to instantiate the registries from python
    /// using the __init__ method. Given that the registries are instantiated in python and some of the
    /// inner working require an async runtime, the new method will create a new tokio runtime into an Arc so that
    /// it can be shared, cloned and used across the different registries in order to prevent deadlocks.
    #[new]
    #[instrument(skip_all)]
    pub fn new() -> Result<Self, RegistryError> {
        let experiment = CardRegistry::rust_new(&RegistryType::Experiment)?;
        let model = CardRegistry::rust_new(&RegistryType::Model)?;
        let data = CardRegistry::rust_new(&RegistryType::Data)?;
        let prompt = CardRegistry::rust_new(&RegistryType::Prompt)?;
        let service = CardRegistry::rust_new(&RegistryType::Service)?;
        let mcp = CardRegistry::rust_new(&RegistryType::Mcp)?;
        let agent = CardRegistry::rust_new(&RegistryType::Agent)?;

        Ok(Self {
            experiment,
            model,
            data,
            prompt,
            service,
            mcp,
            agent,
        })
    }
}
