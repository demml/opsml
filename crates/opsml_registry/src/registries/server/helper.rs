#[cfg(feature = "server")]
use opsml_settings::config::DatabaseSettings;

#[cfg(feature = "server")]
use opsml_sql::{enums::client::SqlClientEnum, traits::CardLogicTrait};

#[cfg(feature = "server")]
use opsml_types::{SqlType, cards::CardTable, contracts::*};

use pyo3::prelude::*;

#[pyclass]
#[derive(Debug)]
pub struct RegistryTestHelper {}

impl RegistryTestHelper {
    #[cfg(feature = "server")]
    fn create_registry_storage() -> String {
        let current_dir = std::env::current_dir().unwrap();
        // get 2 parents up
        let registry_path = current_dir.join("opsml_registries");

        let string_path = registry_path.to_str().unwrap().to_string();

        // create the registry folder if it does not exist
        if !registry_path.exists() {
            std::fs::create_dir(registry_path).unwrap();
        }

        string_path
    }

    #[cfg(feature = "server")]
    fn get_connection_uri(&self) -> String {
        let current_dir = std::env::current_dir().expect("Failed to get current directory");
        let db_path = current_dir.join("opsml.db");

        format!(
            "sqlite://{}",
            db_path.to_str().expect("Failed to convert path to string")
        )
    }
}

impl Default for RegistryTestHelper {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl RegistryTestHelper {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    #[cfg(feature = "server")]
    pub fn setup(&self) {
        self.cleanup();

        let storage_uri = RegistryTestHelper::create_registry_storage();

        let config = DatabaseSettings {
            connection_uri: self.get_connection_uri(),
            max_connections: 1,
            sql_type: SqlType::Sqlite,
        };

        tokio::runtime::Runtime::new().unwrap().block_on(async {
            let script = include_str!("../../../tests/populate_db.sql");

            let client = SqlClientEnum::new(&config).await.unwrap();

            let _ = client.query(script).await;

            // check records
            let query_args = CardQueryArgs {
                uid: None,
                name: None,
                space: None,
                version: None,
                max_date: None,
                tags: None,
                limit: None,
                sort_by_timestamp: None,
                ..Default::default()
            };
            let cards = client
                .query_cards(&CardTable::Data, &query_args)
                .await
                .unwrap();

            assert_eq!(cards.len(), 10);
        });

        // set tracking uri
        unsafe {
            std::env::set_var("OPSML_TRACKING_URI", config.connection_uri);
            std::env::set_var("OPSML_STORAGE_URI", storage_uri);
        }
    }

    #[cfg(not(feature = "server"))]
    pub fn setup(&self) {
        panic!("RegistryTestHelper is only available with the 'server' feature enabled.");
    }

    #[cfg(feature = "server")]
    pub fn cleanup(&self) {
        let current_dir = std::env::current_dir().unwrap();
        // get 2 parents up

        let db_path = current_dir.join("opsml.db");
        let registry_path = current_dir.join("opsml_registries");

        if db_path.exists() {
            std::fs::remove_file(db_path).unwrap();
        }

        if registry_path.exists() {
            std::fs::remove_dir_all(registry_path).unwrap();
        }

        unsafe {
            std::env::remove_var("OPSML_TRACKING_URI");
            std::env::remove_var("OPSML_STORAGE_URI");
        }
    }
}
