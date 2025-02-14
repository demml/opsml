use std::path::PathBuf;

use crate::enums::OpsmlRegistry;
use opsml_cards::*;
use opsml_colors::Colorize;
use opsml_crypt::{decrypt_directory, decrypt_key, encrypt_directory};
use opsml_error::error::OpsmlError;
use opsml_error::error::RegistryError;
use opsml_error::UtilError;
use opsml_interfaces::SaveKwargs;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::*;
use opsml_types::{
    cards::{CardTable, CardType},
    contracts::*,
};
use opsml_utils::clean_string;
use opsml_utils::uid_to_byte_key;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::sync::{Arc, Mutex};
use tempfile::TempDir;
use tracing::{debug, error, instrument};

fn unwrap_pystring(obj: &Bound<'_, PyAny>, field: &str) -> Result<String, RegistryError> {
    obj.getattr(field)
        .map_err(|e| {
            error!("Failed to get field: {}", e);
            RegistryError::Error("Failed to get field".to_string())
        })?
        .extract::<String>()
        .map_err(|e| {
            error!("Failed to extract field: {}", e);
            RegistryError::Error("Failed to extract field".to_string())
        })
}

pub struct CardArgs {
    pub uid: String,
    pub name: String,
    pub repository: String,
    pub version: String,
    pub card_type: CardType,
    pub uri: PathBuf,
    pub encryption_key: Vec<u8>,
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
    pub fn new(registry_type: RegistryType) -> PyResult<Self> {
        debug!("Creating new registry client");
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
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<()> {
        debug!("Registering card");

        // Wrap all operations in a single block_on to handle async operations
        self.runtime
            .block_on(async {
                let mut args = Self::get_card_args(card)?;

                // Verify card for registration
                Self::verify_card(&card, &mut self.registry, &self.registry_type, &args).await?;

                // register card
                // (1) creates new version
                // (2) Inserts card record into db
                // (3) Creates encryption key and returns it
                let card_response = Self::register_card_with_db(
                    &mut self.registry,
                    &card,
                    &self.registry_type,
                    &args,
                    version_type,
                    pre_tag,
                    build_tag,
                )
                .await?;

                // Update card attributes
                Self::update_card_with_server_response(&card_response, card, &mut args)?;

                // Save artifacts
                Self::save_card_artifacts(card, &mut self.fs, save_kwargs, &args).await?;

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

        let card = self.list_cards(uid, repository, name, version, None, None, None, 1)?;
        if card.cards.is_empty() {
            return Err(OpsmlError::new_err("Card not found".to_string()));
        }

        let card = card.cards.first().unwrap();
        // Wrap all operations in a single block_on to handle async operations
        let card = self
            .runtime
            .block_on(async {
                // 1. Load the card // download the card from storage
                Self::download_card(
                    py,
                    &self.registry_type,
                    &mut self.registry,
                    card,
                    &mut self.fs,
                    &self.runtime,
                    interface,
                )
                .await
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
        args: &mut CardArgs,
    ) -> Result<(), RegistryError> {
        // update uid
        card.setattr("uid", response.uid.clone()).map_err(|e| {
            error!("Failed to set uid: {}", e);
            RegistryError::Error("Failed to set uid".to_string())
        })?;
        args.uid = response.uid.clone();

        // update verions
        card.setattr("version", response.version.clone())
            .map_err(|e| {
                error!("Failed to set version: {}", e);
                RegistryError::Error("Failed to set version".to_string())
            })?;
        args.version = response.version.clone();

        // update path
        args.uri = response.uri.clone();

        // update encryption key
        args.encryption_key = response.encryption_key.clone();

        Ok(())
    }

    fn get_card_args(card: &Bound<'_, PyAny>) -> Result<CardArgs, RegistryError> {
        let uid = unwrap_pystring(card, "uid")?;
        let name = unwrap_pystring(card, "name")?;
        let repository = unwrap_pystring(card, "repository")?;
        let version = unwrap_pystring(card, "version")?;

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

        Ok(CardArgs {
            uid,
            name,
            repository,
            version,
            card_type,
            uri: PathBuf::new(),
            encryption_key: vec![],
        })
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
        args: &CardArgs,
    ) -> Result<(), RegistryError> {
        if registry.check_card_uid(&args.uid).await? {
            return Err(RegistryError::Error(
                "Card already exists in the registry. If updating, use update_card".to_string(),
            ));
        }

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

        if !Self::match_registry_type(&args.card_type, registry_type) {
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
    async fn save_card_artifacts<'py>(
        card: &Bound<'_, PyAny>,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        save_kwargs: Option<SaveKwargs>,
        args: &CardArgs,
    ) -> Result<(), RegistryError> {
        // create temp path for saving
        let encryption_key = Self::get_decrypt_key(&args.uid, &args.encryption_key).await?;

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

        encrypt_directory(&tmp_path, &encryption_key)?;
        fs.lock().unwrap().put(&tmp_path, &args.uri, true).await?;

        println!("✓ {}", Colorize::green("saved card artifacts to storage"));

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
        args: &CardArgs,
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

        // get version
        let version: Option<String> = if args.version == CommonKwargs::BaseVersion.to_string() {
            None
        } else {
            Some(args.version.clone())
        };

        let response = registry
            .create_card(registry_card, version, version_type, pre_tag, build_tag)
            .await?;

        println!(
            "✓ {} - {}/{} - v{}",
            Colorize::green("registered card"),
            args.repository,
            args.name,
            args.version
        );

        debug!(
            "Successfully registered card - {:?} - {:?}/{:?} - v{:?}",
            registry_type, args.repository, args.name, args.version
        );

        Ok(response)
    }

    async fn get_decrypt_key(uid: &str, encryption_key: &[u8]) -> Result<Vec<u8>, RegistryError> {
        // convert uid to byte key (used for card encryption)
        let uid_key = uid_to_byte_key(uid)?;

        Ok(decrypt_key(&uid_key, encryption_key)?)
    }

    async fn download_card<'py>(
        py: Python<'py>,
        registry_type: &RegistryType,
        registry: &mut OpsmlRegistry,
        card: &Card,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        rt: &Arc<tokio::runtime::Runtime>,
        interface: Option<&Bound<'py, PyAny>>,
    ) -> Result<Bound<'py, PyAny>, RegistryError> {
        let decryption_key = registry
            .get_artifact_key(card.uid(), &card.card_type())
            .await?;

        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            RegistryError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        let rpath = card
            .uri()
            .map_err(|e| {
                error!("Failed to get card uri: {}", e);
                RegistryError::Error("Failed to get card uri".to_string())
            })?
            .join(SaveName::Card)
            .with_extension(Suffix::Json);

        // add Card.json to tmp_path and rpath

        let lpath = tmp_path.join(SaveName::Card).with_extension(Suffix::Json);

        fs.lock().unwrap().get(&lpath, &rpath, false).await?;

        decrypt_directory(&tmp_path, &decryption_key)?;

        let json_string = std::fs::read_to_string(&lpath).map_err(|e| {
            error!("Failed to read card json: {}", e);
            UtilError::ReadError
        })?;

        let card = Self::card_from_string(
            py,
            json_string,
            registry_type,
            interface,
            decryption_key,
            fs,
            rt,
        )?;

        Ok(card)
    }

    fn card_from_string<'py>(
        py: Python<'py>,
        card_json: String,
        registry_type: &RegistryType,
        interface: Option<&Bound<'py, PyAny>>,
        decryption_key: Vec<u8>,
        fs: &mut Arc<Mutex<FileSystemStorage>>,
        rt: &Arc<tokio::runtime::Runtime>,
    ) -> Result<Bound<'py, PyAny>, RegistryError> {
        let card = match registry_type {
            RegistryType::Model => {
                let mut card =
                    ModelCard::model_validate_json(py, card_json, interface).map_err(|e| {
                        error!("Failed to validate model card: {}", e);
                        RegistryError::Error(e.to_string())
                    })?;
                card.metadata.decryption_key = Some(decryption_key.to_vec());
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

#[cfg(test)]
mod tests {
    use super::*;
    use opsml_settings::config::DatabaseSettings;
    use opsml_sql::base::SqlClient;
    use opsml_sql::enums::client::SqlClientEnum;

    use std::env;

    fn cleanup() {
        // cleanup delete opsml.db and opsml_registries folder from the current directory
        let current_dir = std::env::current_dir().unwrap();
        // get 2 parents up
        let parent_dir = current_dir.parent().unwrap().parent().unwrap();
        let db_path = parent_dir.join("opsml.db");
        let registry_path = parent_dir.join("opsml_registries");

        if db_path.exists() {
            std::fs::remove_file(db_path).unwrap();
        }

        if registry_path.exists() {
            std::fs::remove_dir_all(registry_path).unwrap();
        }
    }

    fn create_registry_storage() {
        let current_dir = std::env::current_dir().unwrap();
        // get 2 parents up
        let parent_dir = current_dir.parent().unwrap().parent().unwrap();
        let registry_path = parent_dir.join("opsml_registries");

        // create the registry folder if it does not exist
        if !registry_path.exists() {
            std::fs::create_dir(registry_path).unwrap();
        }
    }

    fn get_connection_uri() -> String {
        let current_dir = env::current_dir().expect("Failed to get current directory");
        let parent_dir = current_dir.parent().unwrap().parent().unwrap();
        let db_path = parent_dir.join("opsml.db");

        format!(
            "sqlite://{}",
            db_path.to_str().expect("Failed to convert path to string")
        )
    }

    fn setup() {
        // create opsml_registries folder
        create_registry_storage();

        // create opsml.db and populate it with data
        let config = DatabaseSettings {
            connection_uri: get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        tokio::runtime::Runtime::new().unwrap().block_on(async {
            let client = SqlClientEnum::new(&config).await.unwrap();
            let script = std::fs::read_to_string("tests/populate_db.sql").unwrap();
            client.query(&script).await;
        });

        env::set_var("OPSML_TRACKING_URI", "http://0.0.0.0:3000");
    }

    #[tokio::test]
    async fn test_registry_client_list_cards() {
        cleanup();

        //cleanup();
        setup();

        env::set_var("OPSML_TRACKING_URI", "http://0.0.0.0:3000");
        let mut registry = CardRegistry::new(RegistryType::Data).unwrap();

        // Test mode
        assert_eq!(registry.mode(), RegistryMode::Client);

        // Test table name
        assert_eq!(registry.table_name(), CardTable::Data.to_string());

        // Test list cards
        let cards = registry
            .list_cards(None, None, None, None, None, None, None, 25)
            .unwrap();

        assert_eq!(cards.cards.len(), 10);

        cleanup();
    }
}
