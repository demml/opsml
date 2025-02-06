use crate::saver::model::ModelSaver;
use opsml_cards::CardEnum;
use opsml_error::error::SaveError;
use opsml_interfaces::SaveKwargs;
use pyo3::Python;
use tempfile::TempDir;
use tracing::error;
pub enum CardSaver {
    Data,
    Model,
}

impl CardSaver {
    pub fn save_card(
        py: Python,
        card: &CardEnum,
        save_kwargs: Option<SaveKwargs>,
    ) -> Result<(), SaveError> {
        let tmp_dir = TempDir::new().map_err(|e| {
            error!("Failed to create temporary directory: {}", e);
            SaveError::Error("Failed to create temporary directory".to_string())
        })?;

        let tmp_path = tmp_dir.into_path();

        match card {
            CardEnum::Data(_data_card) => {
                // save data card
                // data_card.save_artifacts(tmp_path)?;
            }
            CardEnum::Model(modelcard) => {
                ModelSaver::save_artifacts(py, modelcard, tmp_path, save_kwargs)?;
                // modelcard.interface.save() -> returns metadata
                // modelcard.get_metadata() -> returns metadata
                // modelcard.save_modelcard
            }
        }

        Ok(())
    }
}
