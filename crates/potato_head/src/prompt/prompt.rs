use crate::error::PotatoError;
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig, SanitizationResult};
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde::ser::SerializeSeq;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Prompt {
    #[pyo3(get, set)]
    pub model: String,
    pub prompt: Vec<String>,

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

    pub system_prompt: Vec<String>,
}

fn serialize_as_empty_vec<S>(_: &Vec<SanitizationResult>, serializer: S) -> Result<S::Ok, S::Error>
where
    S: serde::Serializer,
{
    // Always serialize as an empty vector
    serializer.serialize_seq(Some(0))?.end()
}

fn parse_messages_from_pyobject(prompt: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    if !prompt.is_instance_of::<PyList>() {
        // assert string and then convert to vec
        let prompt = prompt
            .extract::<String>()
            .map_err(|_| PotatoError::Error("Prompt must be a list of strings".to_string()))?;
        return Ok(vec![prompt]);
    }

    let prompt = prompt
        .extract::<Vec<String>>()
        .map_err(|_| PotatoError::Error("Prompt must be a list of strings".to_string()))?;
    Ok(prompt)
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
            parse_messages_from_pyobject(system_prompt)?
        } else {
            Vec::new()
        };

        // get version from crate
        let version = env!("CARGO_PKG_VERSION").to_string();

        // Create a sanitizer if sanitization_config is provided
        let sanitizer = sanitization_config.clone().map(PromptSanitizer::new);

        Ok(Self {
            model: model.to_string(),
            prompt: parse_messages_from_pyobject(prompt)?,
            sanitization_config,
            sanitizer,
            sanitized_results: Vec::new(),
            has_sanitize_error: false,
            version,
            system_prompt,
        })
    }
}
