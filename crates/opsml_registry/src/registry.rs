use crate::enums::OpsmlRegistry;
use crate::saver::enums::CardSaver;
use opsml_cards::*;
use opsml_colors::Colorize;
use opsml_error::error::OpsmlError;
use opsml_error::error::RegistryError;
use opsml_interfaces::SaveKwargs;
use opsml_semver::VersionType;
use opsml_types::*;
use opsml_types::{cards::CardTable, contracts::*};
use pyo3::prelude::*;
use tracing::{debug, error, info, instrument};
use uuid::Uuid;

#[pyclass]
#[derive(Debug)]
pub struct CardRegistry {
    registry_type: RegistryType,
    table_name: String,
    registry: OpsmlRegistry,
    runtime: tokio::runtime::Runtime,
}

#[pymethods]
impl CardRegistry {
    #[new]
    pub fn new(registry_type: RegistryType) -> PyResult<Self> {
        // Create a new tokio runtime for the registry (needed for async calls)
        let rt = tokio::runtime::Runtime::new().unwrap();

        let registry = rt
            .block_on(async { OpsmlRegistry::new(registry_type.clone()).await })
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(Self {
            registry_type: registry_type.clone(),
            table_name: CardTable::from_registry_type(&registry_type).to_string(),
            registry,
            runtime: rt,
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

    pub fn mode(&self) -> RegistryMode {
        self.registry.mode()
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (uid=None, name=None, repository=None, version=None, max_date=None, tags=None, limit=None, sort_by_timestamp=None))]
    #[instrument(skip_all)]
    pub fn list_cards(
        &mut self,
        uid: Option<String>,
        name: Option<String>,
        repository: Option<String>,
        version: Option<String>,
        max_date: Option<String>,
        tags: Option<Vec<String>>,
        limit: Option<i32>,
        sort_by_timestamp: Option<bool>,
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

        let limit_check = [
            uid.is_some(),
            name.is_some(),
            repository.is_some(),
            version.is_some(),
            tags.is_some(),
        ];

        // check if any value is true. If not, set limit to 25
        let limit = if limit_check.iter().any(|&x| x) {
            limit
        } else {
            Some(25)
        };

        let query_args = CardQueryArgs {
            uid,
            name,
            repository,
            version,
            max_date,
            tags,
            limit,
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
        // card comes is
        let py = card.py();

        let mut card = CardEnum::from_py(card)?;

        // verify card arguments
        self.verify_card(&card)?;

        // check for needed dependencies
        self.check_dependencies(py, &card)?;

        // check if card and registry type match
        if !card.match_registry_type(&self.registry_type) {
            error!("Card and registry type do not match");
            return Err(OpsmlError::new_err("Card and registry type do not match"));
        }

        let msg = Colorize::green("verified card").to_string();
        println!("✓ {:?}", msg);

        // get next version
        self.set_card_version(&mut card, version_type, pre_tag, build_tag)?;

        let msg = Colorize::green("set card version").to_string();
        println!("✓ {:?}", msg);

        card.update_uid(Uuid::new_v4().to_string());
        card.save_card(py, save_kwargs)?;

        let msg = Colorize::green("saved card artifacts to storage").to_string();
        println!("✓ {:?}", msg);

        // register card
        // get registry record

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
    }
}

impl CardRegistry {
    pub fn set_card_version(
        &mut self,
        card: &mut CardEnum,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
    ) -> Result<(), RegistryError> {
        debug!("Setting card version");

        let version = card.version();

        let card_version: Option<String> = if version == CommonKwargs::BaseVersion.to_string() {
            None
        } else {
            Some(version.to_string())
        };

        // get next version
        let version = self
            .runtime
            .block_on(async {
                self.registry
                    .get_next_version(
                        card.name(),
                        card.repository(),
                        card_version,
                        version_type,
                        pre_tag,
                        build_tag,
                    )
                    .await
            })
            .map_err(|e| RegistryError::Error(e.to_string()))?;

        card.update_version(&version);

        Ok(())
    }

    pub fn verify_card(&mut self, card: &CardEnum) -> Result<(), RegistryError> {
        card.verify_card_for_registration()
            .map_err(|e| RegistryError::Error(e.to_string()))?;

        // if card is a model card and has datacard
        if let CardEnum::Model(model_card) = card {
            if let Some(datacard_uid) = &model_card.metadata.datacard_uid {
                let exists = self.runtime.block_on(async {
                    self.registry
                        .check_card_uid(datacard_uid)
                        .await
                        .map_err(|e| RegistryError::Error(e.to_string()))
                })?;

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

    fn check_dependencies(&self, py: Python, card: &CardEnum) -> Result<(), RegistryError> {
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
            .list_cards(None, None, None, None, None, None, None, None, None)
            .unwrap();

        assert_eq!(cards.cards.len(), 10);

        cleanup();
    }
}
