use crate::enums::OpsmlRegistry;
use opsml_cards::*;
use opsml_colors::Colorize;
use opsml_error::error::OpsmlError;
use opsml_error::error::RegistryError;
use opsml_interfaces::SaveKwargs;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::*;
use opsml_types::{cards::CardTable, contracts::*};
use pyo3::prelude::*;
use tempfile::TempDir;
use tracing::{debug, error, info, instrument};
use uuid::Uuid;

#[pyclass]
pub struct CardRegistry {
    registry_type: RegistryType,
    table_name: String,
    registry: OpsmlRegistry,
    runtime: tokio::runtime::Runtime,
    pub fs: FileSystemStorage,
}

#[pymethods]
impl CardRegistry {
    #[new]
    #[instrument(skip_all)]
    pub fn new(registry_type: RegistryType) -> PyResult<Self> {
        debug!("Creating new registry client");
        // Create a new tokio runtime for the registry (needed for async calls)
        let rt = tokio::runtime::Runtime::new().unwrap();

        let (registry, fs) = rt
            .block_on(async {
                let mut settings = OpsmlConfig::default().storage_settings()?;
                let registry = OpsmlRegistry::new(registry_type.clone()).await?;
                let fs = FileSystemStorage::new(&mut settings).await?;

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
        let mut name = name;
        let mut repository = repository;
        let version = version;
        let tags = tags;

        if name.is_some() {
            name = Some(name.unwrap().to_lowercase());
        }

        if repository.is_some() {
            repository = Some(repository.unwrap().to_lowercase());
        }

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

    #[pyo3(signature = (card, version_type, pre_tag="rc".to_string(), build_tag="build".to_string(), save_kwargs=None))]
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
                // Verify card first
                let py = card.py();
                let mut card = CardEnum::from_py(card).unwrap();

                Self::verify_card(&card, &mut self.registry).await?;

                // Check dependencies
                Self::check_dependencies(py, &card)?;

                // Check registry type match
                if !card.match_registry_type(&self.registry_type) {
                    error!("Card and registry type do not match");
                    return Err(RegistryError::Error(
                        "Card and registry type do not match".to_string(),
                    ));
                }

                let msg = Colorize::green("verified card").to_string();
                println!("✓ {:?}", msg);

                // Set version
                Self::set_card_version(
                    &mut card,
                    version_type,
                    pre_tag,
                    build_tag,
                    &mut self.registry,
                )
                .await?;

                // Update UUID
                card.update_uid(Uuid::new_v4().to_string());

                // Save artifacts
                Self::save_card_artifacts(
                    py,
                    &mut card,
                    &mut self.registry,
                    &mut self.fs,
                    save_kwargs,
                )
                .await?;

                let msg = Colorize::green("registered card").to_string();
                println!("✓ {:?}", msg);

                info!(
                    "Successfully registered card - {:?} - {:?}/{:?} - v{:?}",
                    self.registry_type,
                    card.name(),
                    card.repository(),
                    card.version()
                );

                Ok(())
            })
            .map_err(|e| OpsmlError::new_err(e.to_string()))
    }
}

impl CardRegistry {
    async fn set_card_version(
        card: &mut CardEnum,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
        registry: &mut OpsmlRegistry,
    ) -> Result<(), RegistryError> {
        debug!("Setting card version");

        let version = card.version();

        let card_version: Option<String> = if version == CommonKwargs::BaseVersion.to_string() {
            None
        } else {
            Some(version.to_string())
        };

        // get next version
        let version = registry
            .get_next_version(
                card.name(),
                card.repository(),
                card_version,
                version_type,
                pre_tag,
                build_tag,
            )
            .await?;

        card.update_version(&version);

        let msg = Colorize::green("set card version").to_string();
        println!("✓ {:?}", msg);

        Ok(())
    }

    pub async fn verify_card(
        card: &CardEnum,
        registry: &mut OpsmlRegistry,
    ) -> Result<(), RegistryError> {
        card.verify_card_for_registration()
            .map_err(|e| RegistryError::Error(e.to_string()))?;

        // if card is a model card and has datacard
        if let CardEnum::Model(model_card) = card {
            if let Some(datacard_uid) = &model_card.metadata.datacard_uid {
                let exists = registry.check_card_uid(datacard_uid).await?;

                if !exists {
                    return Err(RegistryError::Error(
                        "Datacard does not exist in the registry".to_string(),
                    ));
                }
            }
        }

        debug!("Verified card");

        Ok(())
    }

    fn check_dependencies(py: Python, card: &CardEnum) -> Result<(), RegistryError> {
        if let CardEnum::Model(modelcard) = card {
            if modelcard.to_onnx {
                let find_spec = py
                    .import("importlib")
                    .unwrap()
                    .getattr("util")
                    .unwrap()
                    .getattr("find_spec")
                    .unwrap();

                let exists = find_spec.call1(("onnx",)).unwrap().is_none();

                if !exists {
                    return Err(RegistryError::Error(
                    "To convert a model to onnx, please install onnx via one of the extras
                    (opsml[sklearn_onnx], opsml[tf_onnx], opsml[torch_onnx]) or set to_onnx to False.
                    ".to_string(),
                ));
                }
            }
        }

        debug!("Checked dependencies");

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
    async fn save_card_artifacts<'py>(
        py: Python<'py>,
        card: &mut CardEnum,
        registry: &mut OpsmlRegistry,
        fs: &mut FileSystemStorage,
        save_kwargs: Option<SaveKwargs>,
    ) -> Result<(), RegistryError> {
        let encrypt_key = registry
            .create_artifact_key(card.uid(), &card.card_type())
            .await?;

        // create temp path for saving
        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            RegistryError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        card.save_card(py, &tmp_path, &encrypt_key, save_kwargs)
            .map_err(|e| {
                error!("Failed to save card: {}", e);
                RegistryError::Error(e.to_string())
            })?;

        fs.put(&tmp_path, &card.uri(), true).await?;

        let msg = Colorize::green("saved card artifacts to storage").to_string();
        println!("✓ {:?}", msg);

        Ok(())
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
