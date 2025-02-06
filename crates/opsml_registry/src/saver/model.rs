use opsml_cards::ModelCard;

use opsml_error::error::SaveError;
use opsml_interfaces::ModelInterfaceMetadata;
use opsml_interfaces::ModelInterfaceSaveMetadata;
use opsml_interfaces::SaveKwargs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;
use tracing::{error, instrument};

pub struct ModelSaver {}

impl ModelSaver {
    #[instrument(skip(py, card, lpath, save_kwargs))]
    pub fn save_artifacts(
        py: Python,
        card: &ModelCard,
        lpath: PathBuf,
        save_kwargs: Option<SaveKwargs>,
    ) -> Result<ModelInterfaceSaveMetadata, SaveError> {
        let _rpath = card.uri();

        let metadata = card
            .interface
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method1("save", (lpath, card.to_onnx, save_kwargs))
            .map_err(|e| {
                error!("Failed to save model artifacts: {}", e);
                SaveError::Error("Failed to save model artifacts".to_string())
            })?;

        let metadata = metadata
            .extract::<ModelInterfaceSaveMetadata>()
            .map_err(|e| {
                error!("Failed to extract metadata: {}", e);
                SaveError::Error("Failed to extract metadata".to_string())
            })?;

        Ok(metadata)

        // create te
    }
}
