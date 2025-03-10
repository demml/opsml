pub mod data;
pub mod experiment;
pub mod model;
pub mod prompt;

pub use data::*;
pub use experiment::*;
pub use model::*;
pub use opsml_error::CardError;
use opsml_types::RegistryType;
pub use prompt::*;
use std::path::Path;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub enum Card {
    Data(DataCard),
    Model(ModelCard),
    Prompt(PromptCard),
    Experiment(ExperimentCard),
}

impl Card {
    pub fn from_file(file_path: &Path, registry_type: &RegistryType) -> Result<Card, CardError> {
        let file =
            std::fs::read_to_string(file_path).map_err(|e| CardError::Error(e.to_string()))?;
        let card: Card = match registry_type {
            RegistryType::Data => {
                serde_json::from_str(&file).map_err(|e| CardError::Error(e.to_string()))?
            }
            RegistryType::Model => {
                serde_json::from_str(&file).map_err(|e| CardError::Error(e.to_string()))?
            }
            RegistryType::Prompt => {
                serde_json::from_str(&file).map_err(|e| CardError::Error(e.to_string()))?
            }
            RegistryType::Experiment => {
                serde_json::from_str(&file).map_err(|e| CardError::Error(e.to_string()))?
            }

            _ => {
                return Err(CardError::Error("Invalid registry type".to_string()));
            }
        };
        Ok(card)
    }
}
