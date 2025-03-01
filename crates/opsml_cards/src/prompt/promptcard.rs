use chrono::NaiveDateTime;
use opsml_error::error::{CardError, OpsmlError};
use opsml_types::{cards::BaseArgs, RegistryType, SaveName, Suffix};
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use potato_lib::ChatPrompt;
use potato_lib::PromptType;
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tracing::error;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum Prompt {
    Chat(ChatPrompt),
}

impl Prompt {
    pub fn save_prompt(&self, path: PathBuf) -> Result<(), CardError> {
        // each enum variant has a save_prompt method
        match self {
            Prompt::Chat(chat_prompt) => {
                let card_save_path = path.join(SaveName::Prompt).with_extension(Suffix::Json);
                PyHelperFuncs::save_to_json(chat_prompt, &card_save_path)?;

                Ok(())
            }
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct PromptCardMetadata {
    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PromptCard {
    pub prompt: Prompt,

    #[pyo3(get, set)]
    pub repository: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Vec<String>,

    #[pyo3(get, set)]
    pub metadata: PromptCardMetadata,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: NaiveDateTime,
}

#[pymethods]
impl PromptCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (prompt, repository=None, name=None, version=None, uid=None, tags=None))]
    pub fn new(
        prompt: &Bound<'_, PyAny>,
        repository: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
    ) -> PyResult<Self> {
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t
                .extract::<Vec<String>>()
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
        };

        let base_args = BaseArgs::create_args(name, repository, version, uid).map_err(|e| {
            error!("Failed to create base args: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;

        let prompt_type = prompt
            .getattr("prompt_type")
            .map_err(|e| OpsmlError::new_err(e.to_string()))?
            .extract::<PromptType>()
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        let prompt = match &prompt_type {
            PromptType::Chat => {
                // extract prompt into ChatPrompt
                let chat_prompt = prompt
                    .extract::<ChatPrompt>()
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?;

                Prompt::Chat(chat_prompt)
            }
            _ => {
                return Err(OpsmlError::new_err("Invalid prompt type"));
            }
        };

        Ok(Self {
            prompt,
            repository: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            metadata: PromptCardMetadata::default(),
            registry_type: RegistryType::Prompt,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
        })
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<&str> {
        self.metadata.experimentcard_uid.as_deref()
    }

    #[setter]
    pub fn set_experimentcard_uid(&mut self, experimentcard_uid: Option<&str>) {
        self.metadata.experimentcard_uid = experimentcard_uid.map(|s| s.to_string());
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        // save model interface
        // if option raise error
        self.prompt.save_prompt(path.clone())?;

        // save modelcard
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> PyResult<PromptCard> {
        serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            OpsmlError::new_err(e.to_string())
        })
    }
}
