use opsml_cards::ModelCard;

use opsml_error::error::SaveError;
use opsml_interfaces::ModelInterfaceMetadata;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;
use tracing::error;

pub struct ModelSaver {}

impl ModelSaver {
    pub fn save_artifacts(py: Python, card: &ModelCard, lpath: PathBuf) -> Result<(), SaveError> {
        let _rpath = card.uri();

        // save artifacts
        let py_dict = PyDict::new(py);
        py_dict.set_item("path", lpath).unwrap();
        py_dict.set_item("to_onnx", card.to_onnx).unwrap();

        let save_args: ModelInterfaceMetadata = card
            .interface
            .call_method(py, "save_interface_artifacts", (), Some(&py_dict))
            .and_then(|result| result.extract(py))
            .map_err(|e| {
                error!(
                    "Failed to save interface artifacts or extract ModelInterfaceSaveArgs: {}",
                    e
                );
                SaveError::Error(
                    "Failed to save interface artifacts or extract ModelInterfaceSaveArgs"
                        .to_string(),
                )
            })?;

        Ok(())

        // create te
    }
}
