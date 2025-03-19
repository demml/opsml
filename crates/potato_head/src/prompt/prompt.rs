use crate::error::PotatoHeadError;
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig};
use crate::prompt::types::{Message, Messages};
use opsml_types::SaveName;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Prompt {
    #[pyo3(get, set)]
    pub model: String,

    #[pyo3(get)]
    pub prompt: Messages,

    #[pyo3(get)]
    pub system_prompt: Messages,

    #[pyo3(get)]
    pub sanitization_config: Option<SanitizationConfig>,

    #[serde(skip)] // skip serialization and deserialization (added when loading from json)
    pub sanitizer: Option<PromptSanitizer>,

    pub version: String,
}

fn parse_prompt(prompt: &Bound<'_, PyAny>) -> PyResult<Messages> {
    let mut prompt_vec = Vec::new();

    // Try to iterate - if it succeeds, it's a sequence
    match prompt.try_iter() {
        Ok(iterator) => {
            // Handle sequence case (list, tuple, etc)
            for element in iterator {
                let element = element?;
                let message = Message::new(&element)?;
                prompt_vec.push(message);
            }
        }
        Err(_) => {
            // Handle single item case
            let message = Message::new(prompt)?;
            prompt_vec.push(message);
        }
    }

    Ok(Messages::new(prompt_vec))
}

#[pymethods]
impl Prompt {
    #[new]
    #[pyo3(signature = (model, prompt, system_prompt=None, sanitization_config=None))]
    pub fn new(
        model: &str,
        prompt: &Bound<'_, PyAny>,
        system_prompt: Option<&Bound<'_, PyAny>>,
        sanitization_config: Option<SanitizationConfig>,
    ) -> PyResult<Self> {
        // extract messages

        let system_prompt = if let Some(system_prompt) = system_prompt {
            parse_prompt(system_prompt)?
        } else {
            Messages::new(Vec::new())
        };

        // get version from crate
        let version = env!("CARGO_PKG_VERSION").to_string();

        // Create a sanitizer if sanitization_config is provided
        let sanitizer = sanitization_config.clone().map(PromptSanitizer::new);

        let prompt = parse_prompt(prompt)?;
        Ok(Self {
            model: model.to_string(),
            prompt: prompt.clone(),
            sanitization_config,
            sanitizer,
            version,
            system_prompt,
        })
    }

    #[pyo3(signature = (path = None))]
    pub fn save_prompt(&self, path: Option<PathBuf>) -> PyResult<PathBuf> {
        let path = path.unwrap_or_else(|| PathBuf::from(SaveName::Prompt));
        PyHelperFuncs::save_to_json(self, &path)?;
        Ok(path)
    }

    #[staticmethod]
    pub fn load_from_path(path: PathBuf) -> PyResult<Self> {
        // Load the JSON file from the path
        let file = std::fs::read_to_string(&path)
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to read file: {}", e)))?;

        // Parse the JSON file into a ChatPrompt
        serde_json::from_str(&file)
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to parse JSON: {}", e)))
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> PyResult<Self> {
        let json_value: Value = serde_json::from_str(&json_string)
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to parse JSON string: {}", e)))?;
        let mut model: Self = serde_json::from_value(json_value)
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to parse JSON value: {}", e)))?;

        // if model has sanitization_config, create a sanitizer
        if let Some(config) = &model.sanitization_config {
            model.sanitizer = Some(PromptSanitizer::new(config.clone()));
        }

        Ok(model)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }
}
