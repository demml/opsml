use crate::error::{PotatoError, PotatoHeadError};
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig, SanitizationResult};
use crate::prompt::types::Message;
use opsml_types::SaveName;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::ser::SerializeSeq;
use serde::{Deserialize, Serialize};
use std::borrow::Cow;

use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Prompt {
    #[pyo3(get, set)]
    pub model: String,

    pub prompt: Vec<Message>,

    #[pyo3(get)]
    pub sanitization_config: Option<SanitizationConfig>,

    #[serde(skip)] // skip serialization and deserialization (added when loading from json)
    pub sanitizer: Option<PromptSanitizer>,

    #[serde(serialize_with = "serialize_as_empty_vec", default = "Vec::new")]
    #[pyo3(get)]
    pub sanitized_results: Vec<SanitizationResult>,

    #[pyo3(get)]
    pub has_sanitize_error: bool,

    pub version: String,

    pub system_prompt: Vec<Message>,

    original_prompt: Vec<Message>,
}

fn serialize_as_empty_vec<S>(_: &Vec<SanitizationResult>, serializer: S) -> Result<S::Ok, S::Error>
where
    S: serde::Serializer,
{
    // Always serialize as an empty vector
    serializer.serialize_seq(Some(0))?.end()
}

fn parse_prompt(prompt: &Bound<'_, PyAny>) -> PyResult<Vec<Message>> {
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

    Ok(prompt_vec)
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
            Vec::new()
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
            has_sanitize_error: false,
            version,
            sanitized_results: Vec::new(),
            system_prompt,
            original_prompt: prompt,
        })
    }

    #[getter]
    fn prompt<'py>(&self, py: Python<'py>) -> PyResult<Vec<Bound<'py, PyAny>>> {
        // iterate over prompt and convert to pyobjects
        self.prompt
            .iter()
            .map(|message| message.to_pyobject(py))
            .collect()
    }

    #[getter]
    fn system_prompt<'py>(&self, py: Python<'py>) -> PyResult<Vec<Bound<'py, PyAny>>> {
        // iterate over prompt and convert to pyobjects
        self.system_prompt
            .iter()
            .map(|message| message.to_pyobject(py))
            .collect()
    }

    pub fn reset(&mut self) -> PyResult<()> {
        self.prompt = self.original_prompt.clone();
        for message in &mut self.prompt {
            message.reset_binding();
        }
        self.has_sanitize_error = false;
        self.sanitized_results.clear();

        Ok(())
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
}

impl Prompt {
    /// Sanitize the message using the provided sanitizer
    /// If no sanitizer is provided, return the original message
    ///
    /// Returns the sanitized message
    ///
    fn sanitize_message<'a>(&mut self, message: &'a str) -> Result<Cow<'a, str>, PotatoError> {
        if let Some(sanitizer) = &self.sanitizer {
            let result = if sanitizer.config.sanitize {
                sanitizer.sanitize(message)?
            } else {
                sanitizer.assess_risk(message)?
            };

            if result.risk_level >= sanitizer.config.risk_threshold {
                self.has_sanitize_error = true;
            }

            let sanitized = result.sanitized_text.clone();
            self.sanitized_results.push(result);

            return Ok(Cow::Owned(sanitized));
        }

        // No need to clone the original message
        Ok(Cow::Borrowed(message))
    }
}
