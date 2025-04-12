use crate::error::PotatoHeadError;
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig};
use crate::prompt::types::Message;
use opsml_types::SaveName;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyString, PyTuple};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Prompt {
    #[pyo3(get, set)]
    pub model: String,

    #[pyo3(get)]
    pub prompt: Vec<Message>,

    #[pyo3(get)]
    pub system_prompt: Vec<Message>,

    #[pyo3(get)]
    pub sanitization_config: Option<SanitizationConfig>,

    #[serde(skip)] // skip serialization and deserialization (added when loading from json)
    pub sanitizer: Option<PromptSanitizer>,

    pub version: String,
}

fn parse_prompt(prompt: &Bound<'_, PyAny>) -> PyResult<Vec<Message>> {
    if prompt.is_instance_of::<Message>() {
        return Ok(vec![prompt.extract::<Message>()?]);
    }

    if prompt.is_instance_of::<PyString>() {
        return Ok(vec![Message::new(prompt)?]);
    }

    let initial_capacity = prompt.len().unwrap_or(1);
    let mut messages = Vec::with_capacity(initial_capacity);

    // Explicitly check for list or tuple
    if prompt.is_instance_of::<PyList>() || prompt.is_instance_of::<PyTuple>() {
        for item in prompt.try_iter()? {
            match item {
                Ok(item) => {
                    messages.push(if item.is_instance_of::<Message>() {
                        item.extract::<Message>()?
                    } else {
                        Message::new(&item)?
                    });
                }
                Err(e) => {
                    return Err(e);
                }
            }
        }
        Ok(messages)
    } else {
        // Not a list or tuple, try to convert directly to Message
        Ok(vec![Message::new(prompt)?])
    }
}

#[pymethods]
impl Prompt {
    #[new]
    #[pyo3(signature = (model, prompt=None, system_prompt=None, sanitization_config=None))]
    pub fn new(
        model: &str,
        prompt: Option<&Bound<'_, PyAny>>,
        system_prompt: Option<&Bound<'_, PyAny>>,
        sanitization_config: Option<SanitizationConfig>,
    ) -> PyResult<Self> {
        // extract messages

        let system_prompt = if let Some(system_prompt) = system_prompt {
            parse_prompt(system_prompt)?
        } else {
            vec![]
        };

        let prompt = if let Some(prompt) = prompt {
            parse_prompt(prompt)?
        } else {
            vec![]
        };

        // if system_prompt and prompt are empty, return error
        if prompt.is_empty() && system_prompt.is_empty() {
            return Err(PotatoHeadError::new_err(
                "Prompt and system prompt cannot be empty. At least one must be
                supplied"
                    .to_string(),
            ));
        }

        // get version from crate
        let version = env!("CARGO_PKG_VERSION").to_string();

        // Create a sanitizer if sanitization_config is provided, else create default sanitizer (will be skipped)
        let sanitizer = sanitization_config
            .as_ref()
            .map(|config| PromptSanitizer::new(config.clone()));

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
        let save_path = path.unwrap_or_else(|| PathBuf::from(SaveName::Prompt));
        PyHelperFuncs::save_to_json(self, &save_path)?;
        Ok(save_path)
    }

    #[staticmethod]
    pub fn load_from_path(path: PathBuf) -> PyResult<Self> {
        // Load the JSON file from the path
        let file = std::fs::read_to_string(&path)
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to read file: {}", e)))?;

        // Parse the JSON file into a Prompt
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

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[getter]
    pub fn sanitizer(&self) -> PyResult<PromptSanitizer> {
        // error if sanitizer is None
        self.sanitizer
            .as_ref()
            .cloned()
            .ok_or_else(|| PotatoHeadError::new_err("Sanitizer is not available".to_string()))
    }
}
