use crate::error::PotatoError;
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig};
use crate::prompt::types::UserContent;
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Prompt {
    #[pyo3(get, set)]
    pub model: String,

    pub prompt: Vec<UserContent>,

    #[pyo3(get)]
    pub sanitization_config: Option<SanitizationConfig>,

    #[serde(skip)] // skip serialization and deserialization (added when loading from json)
    pub sanitizer: Option<PromptSanitizer>,

    #[pyo3(get)]
    pub has_sanitize_error: bool,

    pub version: String,

    #[pyo3(get)]
    pub system_prompt: Vec<String>,
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

fn parse_prompt(prompt: &Bound<'_, PyAny>) -> PyResult<Vec<UserContent>> {
    let mut prompt_vec = Vec::new();

    // Try to iterate - if it succeeds, it's a sequence
    match prompt.try_iter() {
        Ok(iterator) => {
            // Handle sequence case (list, tuple, etc)
            for element in iterator {
                let user_content = UserContent::new(&element?)?;
                prompt_vec.push(user_content);
            }
        }
        Err(_) => {
            // Handle single item case
            let user_content = UserContent::new(prompt)?;
            prompt_vec.push(user_content);
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
            prompt: parse_prompt(prompt)?,
            sanitization_config,
            sanitizer,
            has_sanitize_error: false,
            version,
            system_prompt,
            pydanitc: false,
        })
    }

    #[getter]
    fn prompt<'py>(&self, py: Python<'py>) -> PyResult<Vec<Bound<'py, PyAny>>> {
        // iterate over prompt and convert to pyobjects
        self.prompt
            .iter()
            .map(|content| content.to_pyobject(py))
            .collect()
    }
}
