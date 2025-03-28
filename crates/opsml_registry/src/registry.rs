use crate::enums::OpsmlRegistry;
use crate::enums::RegistryArgs;
use crate::utils::{check_if_card, download_card, upload_card_artifacts, verify_card};
use opsml_client::OpsmlApiClient;
use opsml_colors::Colorize;
use opsml_error::error::OpsmlError;
use opsml_error::error::RegistryError;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_storage::FileSystemStorage;
use opsml_types::*;
use opsml_types::{cards::CardTable, contracts::*};
use opsml_utils::{clean_string, unwrap_pystring};
use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::Arc;
use tempfile::TempDir;
use tokio::sync::Mutex;
use tracing::{debug, error, instrument};

/// Extract registry type from a PyAny object
///
/// # Arguments
///
/// * `registry_type` - PyAny object
///
/// # Returns
///
/// * `Result<RegistryType, OpsmlError>` - Result
///
/// # Errors
///
/// * `OpsmlError` - Error
fn extract_registry_type(registry_type: &Bound<'_, PyAny>) -> PyResult<RegistryType> {
    match registry_type.is_instance_of::<RegistryType>() {
        true => registry_type.extract::<RegistryType>().map_err(|e| {
            error!("Failed to extract registry type: {}", e);
            OpsmlError::new_err(e.to_string())
        }),
        false => {
            let registry_type = registry_type.extract::<String>().unwrap();
            RegistryType::from_string(&registry_type).map_err(|e| {
                error!("Failed to convert string to registry type: {}", e);
                OpsmlError::new_err(e.to_string())
            })
        }
    }
}

pub struct RegistryContext {
    pub registry: OpsmlRegistry,
    pub storage: Arc<Mutex<FileSystemStorage>>,
}

// Helper function to create FileSystemStorage
async fn create_storage(
    settings: &mut OpsmlStorageSettings,
    api_client: Option<OpsmlApiClient>,
) -> Result<FileSystemStorage, RegistryError> {
    FileSystemStorage::new(settings, api_client)
        .await
        .map_err(|e| {
            error!("Failed to create file system storage: {}", e);
            RegistryError::Error(e.to_string())
        })
}

impl RegistryContext {
    pub async fn new(registry_type: RegistryType) -> Result<Self, RegistryError> {
        let config = OpsmlConfig::default();
        let mut storage_settings = config.storage_settings()?;
        let registry_args = RegistryArgs::from_config(&config).await?;

        // Initialize registry and storage concurrently
        let (registry, storage) = tokio::try_join!(
            OpsmlRegistry::new(registry_type, registry_args.clone()),
            create_storage(&mut storage_settings, registry_args.api_client().cloned())
        )?;

        Ok(Self {
            registry,
            storage: Arc::new(Mutex::new(storage)),
        })
    }
}

/// Initialize registry and file system storage
///
///
/// # Arguments
///
/// * `registry_type` - RegistryType
///
/// # Returns
///
/// * `Result<(OpsmlRegistry, Arc<Mutex<FileSystemStorage>>), RegistryError>` - Result
///
/// # Errors
///
/// * `RegistryError` - Error
pub async fn initialize_registry_and_fs(
    registry_type: RegistryType,
) -> Result<(OpsmlRegistry, Arc<Mutex<FileSystemStorage>>), RegistryError> {
    let context = RegistryContext::new(registry_type).await?;
    Ok((context.registry, context.storage))
}

pub struct CardArgs {
    pub uid: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub registry_type: RegistryType,
}

#[pyclass]
#[derive(Clone)]
pub struct CardRegistry {
    registry_type: RegistryType,
    table_name: String,
    pub registry: OpsmlRegistry,
    runtime: Arc<tokio::runtime::Runtime>,
    pub fs: Arc<Mutex<FileSystemStorage>>,
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
    pub fn new(registry_type: &Bound<'_, PyAny>) -> PyResult<Self> {
        debug!("Creating new registry client");

        // check if registry_type is a valid RegistryType or String
        let registry_type = extract_registry_type(registry_type)?;

        // Create a new tokio runtime for the registry (needed for async calls)
        let rt = Arc::new(tokio::runtime::Runtime::new().unwrap());

        let (registry, fs) = rt
            .block_on(async { initialize_registry_and_fs(registry_type.clone()).await })
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(Self {
            registry_type: registry_type.clone(),
            table_name: CardTable::from_registry_type(&registry_type).to_string(),
            registry,
            runtime: rt,
            fs,
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
    #[pyo3(signature = (uid=None, repository=None, name=None,  version=None, max_date=None, tags=None,  sort_by_timestamp=None, limit=25))]
    #[instrument(skip_all)]
    pub fn list_cards(
        &mut self,
        uid: Option<String>,
        repository: Option<String>,
        name: Option<String>,
        version: Option<String>,
        max_date: Option<String>,
        tags: Option<Vec<String>>,
        sort_by_timestamp: Option<bool>,
        limit: i32,
    ) -> PyResult<CardList> {
        debug!(
            "Listing cards - {:?} - {:?} - {:?} - {:?} - {:?} - {:?} - {:?} - {:?}",
            uid, name, repository, version, max_date, tags, limit, sort_by_timestamp
        );

        let name = name.map(|name| clean_string(&name)).transpose()?;

        let repository = repository
            .map(|repository| clean_string(&repository))
            .transpose()?;

        let query_args = CardQueryArgs {
            uid,
            name,
            repository,
            version,
            max_date,
            tags,
            limit: Some(limit),
            sort_by_timestamp,
            registry_type: self.registry_type.clone(),
        };

        let cards = self
            .runtime
            .block_on(async { self.registry.list_cards(query_args).await })
            .map_err(|e| {
                error!("Failed to list cards: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        Ok(CardList { cards })
    }

    #[pyo3(signature = (card, version_type=VersionType::Minor, pre_tag=None, build_tag=None, save_kwargs=None))]
    #[instrument(skip_all)]
    pub fn register_card(
        &mut self,
        card: &Bound<'_, PyAny>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        debug!("Registering card");

        // Wrap all operations in a single block_on to handle async operations
        self.runtime
            .block_on(async {
                Self::verify_and_register_card(
                    card,
                    &mut self.registry,
                    &mut self.fs,
                    version_type,
                    pre_tag,
                    build_tag,
                    save_kwargs,
                    &self.registry_type,
                )
                .await
            })
            .map_err(|e: RegistryError| OpsmlError::new_err(e.to_string()))
    }

    #[pyo3(signature = (uid=None, repository=None, name=None, version=None, interface=None))]
    #[instrument(skip_all)]
    pub fn load_card<'py>(
        &mut self,
        py: Python<'py>,
        uid: Option<String>,
        repository: Option<String>,
        name: Option<String>,
        version: Option<String>,
        interface: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        debug!(
            "Loading card - {:?} - {:?} - {:?} - {:?} - {:?}",
            uid, name, repository, version, interface
        );

        // if uid, name, repository, version is None, return error
        if uid.is_none() && name.is_none() && repository.is_none() && version.is_none() {
            return Err(OpsmlError::new_err(
                "At least one of uid, name, repository, version must be provided".to_string(),
            ));
        }

        // Wrap all operations in a single block_on to handle async operations
        let card = self
            .runtime
            .block_on(async {
                // 1. Load the card // download the card from storage

                let key = self
                    .registry
                    .load_card(CardQueryArgs {
                        uid,
                        name,
                        repository,
                        version,
                        registry_type: self.registry_type.clone(),
                        ..Default::default()
                    })
                    .await?;

                download_card(py, key, &mut self.fs, &self.runtime, interface).await
            })
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(card)
    }

    #[pyo3(signature = (card))]
    #[instrument(skip_all)]
    pub fn delete_card<'py>(&mut self, card: &Bound<'_, PyAny>) -> PyResult<()> {
        debug!("Deleting card");

        check_if_card(card)?;

        self.runtime
            .block_on(async {
                // update card
                Self::_delete_card(&mut self.registry, card, &self.registry_type)
                    .await
                    .map_err(|e| {
                        error!("Failed to delete card: {}", e);
                        e
                    })?;

                Ok(())
            })
            .map_err(|e: RegistryError| OpsmlError::new_err(e.to_string()))
    }

    #[pyo3(signature = (card))]
    #[instrument(skip_all)]
    pub fn update_card<'py>(&mut self, card: &Bound<'_, PyAny>) -> PyResult<()> {
        debug!("Updating card");
        check_if_card(card)?;
        self.runtime
            .block_on(async {
                // update card
                let key = Self::_update_card(&mut self.registry, card, &self.registry_type).await?;

                let tmp_path = Self::save_card(card, &self.registry_type).await?;

                upload_card_artifacts(tmp_path, &mut self.fs, &key).await?;

                Ok(())
            })
            .map_err(|e: RegistryError| OpsmlError::new_err(e.to_string()))
    }
}

impl CardRegistry {
    #[allow(clippy::too_many_arguments)]
    #[instrument(skip_all)]
    async fn verify_and_register_card(
        card: &Bound<'_, PyAny>,
        registry: &mut OpsmlRegistry,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        // Verify card for registration
        debug!("Verifying card");
        verify_card(card, registry_type, registry).await?;

        // Register card
        debug!("Registering card");
        let create_response = Self::_register_card(
            registry,
            card,
            registry_type,
            version_type,
            pre_tag,
            build_tag,
        )
        .await?;

        // Update card attributes
        debug!("Updating card with server response");
        Self::update_card_with_server_response(&create_response, card)?;

        // Save card artifacts to temp path
        debug!("Saving card artifacts");
        let tmp_path = Self::save_card_artifacts(card, save_kwargs, registry_type).await?;

        // Save artifacts
        debug!("Uploading card artifacts");
        upload_card_artifacts(tmp_path, fs, &create_response.key).await?;

        debug!("Successfully registered card");
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
            error!("Failed to set uid: {}", e);
            RegistryError::Error("Failed to set uid".to_string())
        })?;

        // update version
        card.setattr("version", response.version.clone())
            .map_err(|e| {
                error!("Failed to set version: {}", e);
                RegistryError::Error("Failed to set version".to_string())
            })?;

        // update created_at
        card.setattr("created_at", response.created_at)
            .map_err(|e| {
                error!("Failed to set created_at: {}", e);
                RegistryError::Error("Failed to set created_at".to_string())
            })?;

        // update app_env
        card.setattr("app_env", response.app_env.clone())
            .map_err(|e| {
                error!("Failed to set app_env: {}", e);
                RegistryError::Error("Failed to set app_env".to_string())
            })?;

        Ok(())
    }

    /// Save card artifacts to storage
    /// Using a runtime, this method will:
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
    async fn save_card_artifacts(
        card: &Bound<'_, PyAny>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
        registry_type: &RegistryType,
    ) -> Result<PathBuf, RegistryError> {
        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            RegistryError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        match registry_type {
            RegistryType::Experiment | RegistryType::Prompt => {
                card.call_method1("save", (tmp_path.to_path_buf(),))
                    .map_err(|e| {
                        error!("Failed to save card: {}", e);
                        RegistryError::Error(e.to_string())
                    })?;
            }

            _ => {
                card.call_method1("save", (tmp_path.to_path_buf(), save_kwargs))
                    .map_err(|e| {
                        error!("Failed to save card: {}", e);
                        RegistryError::Error(e.to_string())
                    })?;
            }
        }

        Ok(tmp_path)
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
    async fn save_card(
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<PathBuf, RegistryError> {
        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            RegistryError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        match registry_type {
            RegistryType::Experiment => {
                card.call_method1("save", (tmp_path.to_path_buf(),))
                    .map_err(|e| {
                        error!("Failed to save card: {}", e);
                        RegistryError::Error(e.to_string())
                    })?;
            }
            _ => {
                card.call_method1("save_card", (tmp_path.to_path_buf(),))
                    .map_err(|e| {
                        error!("Failed to save card: {}", e);
                        RegistryError::Error(e.to_string())
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
    async fn _register_card(
        registry: &mut OpsmlRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<CreateCardResponse, RegistryError> {
        let registry_card = card
            .call_method0("get_registry_card")
            .map_err(|e| {
                error!("Failed to get registry card: {}", e);
                RegistryError::Error("Failed to get registry card".to_string())
            })?
            .extract::<Card>()
            .map_err(|e| {
                error!("Failed to extract registry card: {}", e);
                RegistryError::Error("Failed to extract registry card".to_string())
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
            .await?;

        println!(
            "{} - {} - {}/{} - v{}",
            Colorize::green("Registered card"),
            Colorize::purple(&registry_type.to_string()),
            response.repository,
            response.name,
            response.version
        );

        debug!(
            "Successfully registered card - {} - {}/{} - v{}",
            registry_type, response.repository, response.name, response.version
        );

        Ok(response)
    }

    #[instrument(skip_all)]
    async fn _delete_card(
        registry: &mut OpsmlRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        let uid = unwrap_pystring(card, "uid")?;
        let repository = unwrap_pystring(card, "repository")?;

        let delete_request = DeleteCardRequest {
            uid,
            repository,
            registry_type: registry_type.clone(),
        };

        registry.delete_card(delete_request).await?;

        println!("{}", Colorize::green("Deleted card"));
        debug!("Successfully deleted card");

        Ok(())
    }

    #[instrument(skip_all)]
    async fn _update_card(
        registry: &mut OpsmlRegistry,
        card: &Bound<'_, PyAny>,
        registry_type: &RegistryType,
    ) -> Result<ArtifactKey, RegistryError> {
        let registry_card = card
            .call_method0("get_registry_card")
            .map_err(|e| {
                error!("Failed to get registry card: {}", e);
                RegistryError::Error("Failed to get registry card".to_string())
            })?
            .extract::<Card>()
            .map_err(|e| {
                error!("Failed to extract registry card: {}", e);
                RegistryError::Error("Failed to extract registry card".to_string())
            })?;

        // update card
        registry.update_card(&registry_card).await.map_err(|e| {
            error!("Failed to update card: {}", e);
            e
        })?;

        // get key to re-save Card.json
        let uid = registry_card.uid().to_string();
        let key = registry
            .load_card(CardQueryArgs {
                uid: Some(uid),
                registry_type: registry_type.clone(),
                ..Default::default()
            })
            .await
            .map_err(|e| {
                error!("Failed to load card: {}", e);
                e
            })?;

        println!(
            "{} - {} - {}/{} - v{}",
            Colorize::green("Updated card"),
            Colorize::purple(&registry_type.to_string()),
            registry_card.repository(),
            registry_card.name(),
            registry_card.version()
        );
        debug!("Successfully updated card");

        Ok(key)
    }
}

impl CardRegistry {
    pub fn rust_new(
        registry_type: &RegistryType,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> Result<Self, RegistryError> {
        let (registry, fs) = rt.block_on(async {
            initialize_registry_and_fs(registry_type.clone())
                .await
                .map_err(|e| RegistryError::Error(e.to_string()))
        })?;

        Ok(Self {
            registry_type: registry_type.clone(),
            table_name: CardTable::from_registry_type(registry_type).to_string(),
            registry,
            runtime: rt,
            fs,
        })
    }

    pub fn update_type(&mut self, registry_type: RegistryType) {
        self.registry_type = registry_type.clone();
        self.table_name = CardTable::from_registry_type(&registry_type).to_string();
        self.registry.update_registry_type(registry_type);
    }
}

#[pyclass]
pub struct CardRegistries {
    #[pyo3(get)]
    pub experiment: CardRegistry,

    #[pyo3(get)]
    pub model: CardRegistry,

    #[pyo3(get)]
    pub data: CardRegistry,

    #[pyo3(get)]
    pub prompt: CardRegistry,

    pub rt: Arc<tokio::runtime::Runtime>,
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
    pub fn new() -> PyResult<Self> {
        let rt = Arc::new(tokio::runtime::Runtime::new().unwrap());

        let experiment = CardRegistry::rust_new(&RegistryType::Experiment, rt.clone())?;

        // clone experiment to create other registries
        let mut model = experiment.clone();
        model.update_type(RegistryType::Model);

        let mut data = experiment.clone();
        data.update_type(RegistryType::Data);

        let mut prompt = experiment.clone();
        prompt.update_type(RegistryType::Prompt);

        Ok(Self {
            experiment,
            model,
            data,
            prompt,
            rt,
        })
    }
}

impl CardRegistries {
    pub fn new_with_rt(rt: Arc<tokio::runtime::Runtime>) -> PyResult<Self> {
        let experiment = CardRegistry::rust_new(&RegistryType::Experiment, rt.clone())?;

        // clone experiment to create other registries
        let mut model = experiment.clone();
        model.update_type(RegistryType::Model);

        let mut data = experiment.clone();
        data.update_type(RegistryType::Data);

        let mut prompt = experiment.clone();
        prompt.update_type(RegistryType::Prompt);

        Ok(Self {
            experiment,
            model,
            data,
            prompt,
            rt,
        })
    }

    // helper for accessing the file system storage
    pub fn get_fs(&self) -> Arc<Mutex<FileSystemStorage>> {
        self.experiment.fs.clone()
    }
}
