use chrono::NaiveDateTime;
use opsml_crypt::decrypt_directory;
use opsml_error::error::{CardError, OpsmlError};
use opsml_types::{
    cards::BaseArgs, DataType, ModelInterfaceType, ModelType, RegistryType, SaveName, Suffix,
    TaskType,
};
use potato_lib::ChatPrompt;
use potato_lib::PromptType;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{debug, error};

enum Prompt {
    Chat(ChatPrompt),
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct PromptCardMetadata {
    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
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
