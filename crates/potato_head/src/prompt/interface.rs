use crate::error::PotatoHeadError;
use crate::prompt::sanitize::{PromptSanitizer, SanitizationConfig};
use crate::prompt::types::Message;
use opsml_types::SaveName;
use opsml_utils::{json_to_pyobject, pyobject_to_json, PyHelperFuncs};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::hash::Hash;
use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelSettings {
    #[pyo3(get, set)]
    pub model: String,

    #[pyo3(get, set)]
    pub provider: String,

    #[pyo3(get, set)]
    pub max_tokens: Option<usize>,

    #[pyo3(get, set)]
    pub temperature: Option<f32>,

    #[pyo3(get, set)]
    pub top_p: Option<f32>,

    #[pyo3(get, set)]
    pub frequency_penalty: Option<f32>,

    #[pyo3(get, set)]
    pub presence_penalty: Option<f32>,

    #[pyo3(get, set)]
    pub timeout: f32,

    #[pyo3(get, set)]
    pub parallel_tool_calls: Option<bool>,

    #[pyo3(get, set)]
    pub seed: Option<u64>,

    #[pyo3(get, set)]
    pub logit_bias: Option<HashMap<String, i32>>,

    #[pyo3(get, set)]
    pub stop_sequences: Option<Vec<String>>,

    pub extra_body: Option<Value>,
}

#[pymethods]
impl ModelSettings {
    #[new]
    #[pyo3(signature = (model, provider, max_tokens=None, temperature=None, top_p=None, frequency_penalty=None, presence_penalty=None, timeout=0.0, parallel_tool_calls=None, seed=None, logit_bias=None, stop_sequences=None, extra_body=None))]
    pub fn new(
        model: &str,
        provider: &str,
        max_tokens: Option<usize>,
        temperature: Option<f32>,
        top_p: Option<f32>,
        frequency_penalty: Option<f32>,
        presence_penalty: Option<f32>,
        timeout: f32,
        parallel_tool_calls: Option<bool>,
        seed: Option<u64>,
        logit_bias: Option<HashMap<String, i32>>,
        stop_sequences: Option<Vec<String>>,
        extra_body: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        // check if extra body is not none.
        // if not none, conver to py any and attempt pyobject_to_json
        let extra_body = if let Some(extra_body) = extra_body {
            Some(pyobject_to_json(extra_body).map_err(|e| {
                PotatoHeadError::new_err(format!("Failed to convert extra body: {}", e))
            })?)
        } else {
            None
        };

        Ok(Self {
            model: model.to_string(),
            provider: provider.to_string(),
            max_tokens,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty,
            timeout,
            parallel_tool_calls,
            seed,
            logit_bias,
            stop_sequences,
            extra_body,
        })
    }

    #[getter]
    pub fn extra_body<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyDict>>> {
        // error if extra body is None
        self.extra_body
            .as_ref()
            .map(|v| {
                let pydict = PyDict::new(py);
                json_to_pyobject(py, v, &pydict)
            })
            .transpose()
            .map_err(|e| PotatoHeadError::new_err(format!("Failed to get extra body: {}", e)))
    }
}

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
            vec![]
        };

        let prompt = parse_prompt(prompt)?;

        // get version from crate
        let version = opsml_version::version();

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
