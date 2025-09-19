use crate::error::RegistryError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_settings::DatabaseSettings;
use opsml_sql::enums::client::get_sql_client;
use opsml_sql::{enums::client::SqlClientEnum, schemas::*, traits::*};
use opsml_types::contracts::evaluation::{
    CreateEvaluationResponse, EvaluationProvider, EvaluationType,
};
use opsml_types::{cards::CardTable, contracts::*, *};
use std::sync::Arc;
#[derive(Debug)]
pub struct ServerEvaluationRegistry {
    sql_client: Arc<SqlClientEnum>,
    pub table_name: CardTable,
    pub storage_settings: OpsmlStorageSettings,
}

impl ServerEvaluationRegistry {
    pub fn mode(&self) -> RegistryMode {
        RegistryMode::Server
    }

    pub fn table_name(&self) -> String {
        self.table_name.to_string()
    }
    pub async fn new(
        storage_settings: OpsmlStorageSettings,
        database_settings: DatabaseSettings,
    ) -> Result<Self, RegistryError> {
        let sql_client = Arc::new(get_sql_client(&database_settings).await?);
        let table_name = CardTable::from_registry_type(&RegistryType::Evaluation);

        Ok(Self {
            sql_client,
            table_name,
            storage_settings,
        })
    }

    pub async fn create_evaluation(
        &self,
        name: String,
        evaluation_type: EvaluationType,
        evaluation_provider: EvaluationProvider,
    ) -> Result<CreateEvaluationResponse, RegistryError> {
        let record = EvaluationSqlRecord::new(name, evaluation_type, evaluation_provider);

        self.sql_client
            .insert_card(&self.table_name, &record)
            .await?;
        Ok(CreateEvaluationResponse { id: record.id })
    }
}
