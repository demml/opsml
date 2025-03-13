use chrono::NaiveDateTime;
use opsml_error::error::{CardError, OpsmlError};
use opsml_types::contracts::{Card, PromptCardClientRecord};
use opsml_types::{cards::BaseArgs, RegistryType, SaveName, Suffix};
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use potato_lib::ChatPrompt;
use potato_lib::PromptType;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::IntoPyObjectExt;
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

    pub fn prompt_type(&self) -> PromptType {
        match self {
            Prompt::Chat(prompt) => prompt.prompt_type.clone(),
        }
    }

    pub fn to_bound_py_any<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        match self {
            Prompt::Chat(prompt) => {
                let chat_prompt = prompt.clone().into_bound_py_any(py)?;
                Ok(chat_prompt)
            }
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct PromptCardMetadata {
    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,
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

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub opsml_version: String,
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
            is_card: true,
            opsml_version: env!("CARGO_PKG_VERSION").to_string(),
        })
    }

    #[getter]
    pub fn prompt<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        self.prompt.to_bound_py_any(py)
    }

    #[setter]
    pub fn set_prompt(&mut self, prompt: &Bound<'_, PyAny>) -> PyResult<()> {
        let prompt_type = prompt
            .getattr("prompt_type")
            .map_err(|e| OpsmlError::new_err(e.to_string()))?
            .extract::<PromptType>()
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        self.prompt = match &prompt_type {
            PromptType::Chat => {
                let chat_prompt = prompt
                    .extract::<ChatPrompt>()
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?;

                Prompt::Chat(chat_prompt)
            }
            _ => {
                return Err(OpsmlError::new_err("Invalid prompt type"));
            }
        };

        Ok(())
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

    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        let record = PromptCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            repository: self.repository.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            prompt_type: self.prompt.prompt_type().to_string(),
            experimentcard_uid: self.metadata.experimentcard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(Card::Prompt(record))
    }

    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }
}
