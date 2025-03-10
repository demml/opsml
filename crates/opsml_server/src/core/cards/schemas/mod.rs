pub mod datacard;
pub mod experimentcard;
pub mod modelcard;

use opsml_cards::PromptCard;
use opsml_error::CardError;
use opsml_types::RegistryType;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Serialize, Deserialize)]
pub enum Card {
    Data(datacard::DataCard),
    Model(modelcard::ModelCard),
    Prompt(PromptCard),
    Experiment(Box<experimentcard::ExperimentCard>),
}

impl Card {
    #[allow(dead_code)]
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
