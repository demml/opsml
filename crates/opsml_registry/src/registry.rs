use crate::enums::OpsmlRegistry;
use opsml_cards::*;
use opsml_colors::Colorize;
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::error::OpsmlError;
use opsml_error::error::RegistryError;
use opsml_error::UtilError;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::*;
use opsml_types::{
    cards::{CardTable, CardType},
    contracts::*,
};
use opsml_utils::{clean_string, unwrap_pystring};
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tempfile::TempDir;

use tracing::{debug, error, instrument};

pub struct CardArgs {
    pub uid: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub card_type: CardType,
}

#[pyclass]
pub struct CardRegistry {
    registry_type: RegistryType,
    table_name: String,
    registry: OpsmlRegistry,
    runtime: Arc<tokio::runtime::Runtime>,
    fs: Arc<Mutex<FileSystemStorage>>,
}

#[pymethods]
impl CardRegistry {
    #[new]
    #[instrument(skip_all)]
    pub fn new(registry_type: &Bound<'_, PyAny>) -> PyResult<Self> {
        debug!("Creating new registry client");

        // check if registry_type is a valid RegistryType or String
        let registry_type = if registry_type.is_instance_of::<RegistryType>() {
            registry_type.extract::<RegistryType>().map_err(|e| {
                error!("Failed to extract registry type: {}", e);
                OpsmlError::new_err(e.to_string())
            })?
        } else {
            let registry_type = registry_type.extract::<String>().unwrap();
            RegistryType::from_string(&registry_type)?
        };

        // Create a new tokio runtime for the registry (needed for async calls)
        let rt = Arc::new(tokio::runtime::Runtime::new().unwrap());

        let (registry, fs) = rt
            .block_on(async {
                let mut settings = OpsmlConfig::default().storage_settings()?;
                let registry = OpsmlRegistry::new(registry_type.clone()).await?;
                let fs = Arc::new(Mutex::new(FileSystemStorage::new(&mut settings).await?));

                Ok::<_, RegistryError>((registry, fs))
            })
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

        let uid = uid;
        let version = version;
        let tags = tags;

        let name = if let Some(name) = name {
            Some(clean_string(&name))
        } else {
            None
        };

        let repository = if let Some(repository) = repository {
            Some(clean_string(&repository))
        } else {
            None
        };

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
                // Verify card for registration
                Self::verify_card(&card, &mut self.registry, &self.registry_type).await?;

                // Save card artifacts to temp path (returns metadata to store in registry)
                let tmp_path = Self::save_card_artifacts(card, save_kwargs).await?;

                // register card
                // (1) creates new version
                // (2) Inserts card record into db
                // (3) Creates encryption key and returns it
                let create_response = Self::register_card_with_db(
                    &mut self.registry,
                    &card,
                    &self.registry_type,
                    version_type,
                    pre_tag,
                    build_tag,
                )
                .await?;

                // Update card attributes
                Self::update_card_with_server_response(&create_response, card)?;

                // Save artifacts
                Self::upload_card_artifacts(tmp_path, &mut self.fs, &create_response).await?;

                Ok(())
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

                Self::download_card(py, key, &mut self.fs, &self.runtime, interface).await
            })
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(card)
    }
}

impl CardRegistry {
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

        // update verions
        card.setattr("version", response.version.clone())
            .map_err(|e| {
                error!("Failed to set version: {}", e);
                RegistryError::Error("Failed to set version".to_string())
            })?;

        Ok(())
    }

    fn match_registry_type(card_type: &CardType, registry_type: &RegistryType) -> bool {
        let matched = match card_type {
            CardType::Data => {
                // assert registryType == RegistryType.Data
                *registry_type == RegistryType::Data
            }
            CardType::Model => {
                // assert registryType == RegistryType.Model
                *registry_type == RegistryType::Model
            }
            _ => {
                return false;
            }
        };

        matched
    }

    #[instrument(skip_all)]
    pub async fn verify_card(
        card: &Bound<'_, PyAny>,
        registry: &mut OpsmlRegistry,
        registry_type: &RegistryType,
    ) -> Result<(), RegistryError> {
        if card.is_instance_of::<ModelCard>() {
            let datacard_uid = card
                .getattr("metadata")
                .unwrap()
                .getattr("datacard_uid")
                .unwrap()
                .extract::<Option<String>>()
                .unwrap();

            if let Some(datacard_uid) = datacard_uid {
                let exists = registry.check_card_uid(&datacard_uid).await?;

                if !exists {
                    return Err(RegistryError::Error(
                        "Datacard does not exist in the registry".to_string(),
                    ));
                }
            }
        }

        let card_type = card
            .getattr("card_type")
            .map_err(|e| {
                error!("Failed to get card type: {}", e);
                RegistryError::Error("Failed to get card type".to_string())
            })?
            .extract::<CardType>()
            .map_err(|e| {
                error!("Failed to extract card type: {}", e);
                RegistryError::Error("Failed to extract card type".to_string())
            })?;

        if !Self::match_registry_type(&card_type, registry_type) {
            return Err(RegistryError::Error(
                "Card and registry type do not match".to_string(),
            ));
        }

        debug!("Verified card");
        println!("✓ {}", Colorize::green("verified card"));

        Ok(())
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
    async fn save_card_artifacts(
        card: &Bound<'_, PyAny>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
    ) -> Result<PathBuf, RegistryError> {
        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            RegistryError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        card.call_method1("save", (tmp_path.to_path_buf(), save_kwargs))
            .map_err(|e| {
                error!("Failed to save card: {}", e);
                RegistryError::Error(e.to_string())
            })?;

        Ok(tmp_path)
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
    async fn upload_card_artifacts(
        path: PathBuf,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        card_record: &CreateCardResponse,
    ) -> Result<(), RegistryError> {
        // create temp path for saving
        let encryption_key = card_record
            .key
            .get_decrypt_key()
            .map_err(|e| RegistryError::Error(e.to_string()))?;

        encrypt_directory(&path, &encryption_key)?;
        fs.lock()
            .unwrap()
            .put(&path, &card_record.key.storage_path(), true)
            .await?;

        println!(
            "...✓ {}",
            Colorize::green("saved card artifacts to storage")
        );

        debug!("Saved card artifacts to storage");

        Ok(())
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
    async fn register_card_with_db(
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
            "...✓ {} - {}/{} - v{}",
            Colorize::green("registered card"),
            response.repository,
            response.name,
            response.version
        );

        debug!(
            "Successfully registered card - {:?} - {:?}/{:?} - v{:?}",
            registry_type, response.repository, response.name, response.version
        );

        Ok(response)
    }

    async fn download_card<'py>(
        py: Python<'py>,
        key: ArtifactKey,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        rt: &Arc<tokio::runtime::Runtime>,
        interface: Option<&Bound<'py, PyAny>>,
        // given uid or (name, repo, versiont)
        // get card uid
        // get artifact_key from registry for a uid
        // get storage_uri
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

        fs.lock().unwrap().get(&lpath, &rpath, false).await?;
        decrypt_directory(&tmp_path, &decryption_key)?;

        let json_string = std::fs::read_to_string(&lpath).map_err(|e| {
            error!("Failed to read card json: {}", e);
            UtilError::ReadError
        })?;

        let card = Self::card_from_string(py, json_string, interface, key, fs, rt)?;

        Ok(card)
    }

    fn card_from_string<'py>(
        py: Python<'py>,
        card_json: String,
        interface: Option<&Bound<'py, PyAny>>,
        key: ArtifactKey,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        rt: &Arc<tokio::runtime::Runtime>,
    ) -> Result<Bound<'py, PyAny>, RegistryError> {
        let card = match key.card_type {
            CardType::Model => {
                let mut card =
                    ModelCard::model_validate_json(py, card_json, interface).map_err(|e| {
                        error!("Failed to validate model card: {}", e);
                        RegistryError::Error(e.to_string())
                    })?;

                card.artifact_key = Some(key);
                card.fs = Some(fs.clone());
                card.rt = Some(rt.clone());

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
}
