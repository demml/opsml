use crate::error::CardError;
use crate::traits::OpsmlCard;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_types::DriftProfileUri;
use opsml_types::contracts::{CardRecord, PromptCardClientRecord};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::{PyHelperFuncs, get_utc_datetime};
use potato_head::prompt_types::Prompt;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use pyo3::types::PyList;
use scouter_client::AssertionTasks;
use scouter_client::TasksFile;
use scouter_client::{DriftType, GenAIEvalConfig, GenAIEvalProfile};
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument};

pub fn deserialize_from_path<T: DeserializeOwned>(path: PathBuf) -> Result<T, CardError> {
    let content = std::fs::read_to_string(&path)?;

    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| CardError::Error(format!("Invalid file path: {:?}", path)))?;

    let item = match extension.to_lowercase().as_str() {
        "json" => serde_json::from_str(&content)?,
        "yaml" | "yml" => serde_yaml::from_str(&content)?,
        _ => {
            return Err(CardError::Error(format!(
                "Unsupported file extension '{}'. Expected .json, .yaml, or .yml",
                extension
            )));
        }
    };

    Ok(item)
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct PromptCardMetadata {
    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    #[pyo3(get)]
    pub drift_profile_uri_map: Option<HashMap<String, DriftProfileUri>>,
}

#[pyclass]
#[derive(Debug, Serialize, Clone)]
pub struct PromptCard {
    pub prompt: Prompt,

    #[pyo3(get, set)]
    pub space: String,

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
    pub created_at: DateTime<Utc>,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub opsml_version: String,

    #[pyo3(get, set)]
    pub eval_profile: Option<GenAIEvalProfile>,
}

impl OpsmlCard for PromptCard {
    fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        self.get_registry_card()
    }

    fn get_version(&self) -> String {
        self.version.clone()
    }

    fn set_name(&mut self, name: String) {
        self.name = name;
    }

    fn set_space(&mut self, space: String) {
        self.space = space;
    }

    fn set_version(&mut self, version: String) {
        self.version = version;
    }

    fn set_uid(&mut self, uid: String) {
        self.uid = uid;
    }

    fn set_created_at(&mut self, created_at: DateTime<Utc>) {
        self.created_at = created_at;
    }

    fn set_app_env(&mut self, app_env: String) {
        self.app_env = app_env;
    }

    fn is_card(&self) -> bool {
        self.is_card
    }

    fn save(&self, path: PathBuf) -> Result<(), CardError> {
        self.save_card(path)
    }

    fn registry_type(&self) -> &RegistryType {
        &self.registry_type
    }
}

#[pymethods]
impl PromptCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (prompt, space=None, name=None, version=None, tags=None, eval_profile=None))]
    pub fn new(
        prompt: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        eval_profile: Option<GenAIEvalProfile>,
    ) -> Result<Self, CardError> {
        let prompt = prompt.extract::<Prompt>().inspect_err(|e| {
            error!("Failed to extract prompt: {e}");
        })?;

        Self::new_rs(prompt, space, name, version, tags, eval_profile)
    }

    #[getter]
    pub fn prompt<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        Ok(self.prompt.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_prompt(&mut self, prompt: &Bound<'_, PyAny>) -> Result<(), CardError> {
        self.prompt = prompt.extract::<Prompt>().inspect_err(|e| {
            error!("Failed to extract prompt: {e}");
        })?;

        Ok(())
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<&str> {
        self.metadata.experimentcard_uid.as_deref()
    }

    #[setter]
    pub fn set_experimentcard_uid(&mut self, experimentcard_uid: Option<String>) {
        self.metadata.experimentcard_uid = experimentcard_uid.map(|s| s.to_string());
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        debug!("Saving PromptCard to path: {:?}", path);

        let eval_profile_uri_map = if let Some(_eval_profile) = &mut self.eval_profile {
            Some(self.save_eval_profile(&path)?)
        } else {
            None
        };

        self.metadata.drift_profile_uri_map = eval_profile_uri_map;

        self.prompt.save_prompt(Some(path.clone()))?;
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> Result<PromptCard, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?)
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = PromptCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            experimentcard_uid: self.metadata.experimentcard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            content_hash: self.calculate_content_hash()?,
        };

        Ok(CardRecord::Prompt(record))
    }

    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    /// Create drift profile
    ///
    /// # Arguments
    ///
    /// * `config` - LLMDriftConfig
    /// * `tasks` - List of tasks (LLMJudgeTask or AssertionTask)
    /// # Returns
    ///
    #[pyo3(signature = (alias, tasks, config=None))]
    pub fn create_eval_profile(
        &mut self,
        alias: String,
        tasks: &Bound<'_, PyList>,
        config: Option<GenAIEvalConfig>,
    ) -> Result<(), CardError> {
        debug!("Creating eval profile");
        self.eval_profile = Some(GenAIEvalProfile::new_py(tasks, config, Some(alias))?);
        Ok(())
    }

    #[pyo3(name = "_update_drift_config_args")]
    fn update_drift_config_args(&mut self) -> Result<(), CardError> {
        if let Some(profile) = &mut self.eval_profile {
            profile.config.name = self.name.clone();
            profile.config.space = self.space.clone();
            profile.config.version = self.version.clone();
        }

        Ok(())
    }

    #[pyo3(name = "_update_eval_uid")]
    fn update_eval_uid(&mut self, uid: String) -> Result<(), CardError> {
        if let Some(profile) = &mut self.eval_profile {
            profile.config.uid = uid;
        }

        Ok(())
    }

    #[staticmethod]
    pub fn from_path(path: PathBuf) -> Result<Self, CardError> {
        deserialize_from_path(path)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, CardError> {
        let mut hasher = Sha256::new();

        // Hash the prompt
        let prompt_string = serde_json::to_string(&self.prompt)?;
        hasher.update(prompt_string.as_bytes());

        // Hash the eval profile, excluding runtime-generated uid
        if let Some(eval_profile) = &self.eval_profile {
            let mut eval_value = serde_json::to_value(eval_profile)?;

            // Remove runtime-generated fields from config
            if let Some(config) = eval_value.get_mut("config")
                && let Some(config_obj) = config.as_object_mut()
            {
                config_obj.remove("uid");
                config_obj.remove("space");
                config_obj.remove("name");
                config_obj.remove("version");
            }

            let eval_string = serde_json::to_string(&eval_value)?;
            hasher.update(eval_string.as_bytes());
        }

        Ok(hasher.finalize().to_vec())
    }
}

#[derive(Debug, Deserialize)]
pub struct EvaluationConfig {
    pub config: Option<GenAIEvalConfig>,
    pub tasks: TasksFile,
    pub alias: String,
}

#[derive(Debug, Deserialize)]
pub struct PromptConfig {
    pub prompt: Prompt,
    #[serde(default)]
    pub space: Option<String>,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub version: Option<String>,
    #[serde(default)]
    pub tags: Option<Vec<String>>,
    #[serde(default)]
    pub evaluation: Option<EvaluationConfig>,
}

impl PromptConfig {
    pub fn into_promptcard(self) -> Result<PromptCard, CardError> {
        let mut card = PromptCard::new_rs(
            self.prompt,
            self.space.as_deref(),
            self.name.as_deref(),
            self.version.as_deref(),
            self.tags,
            None,
        )?;

        if let Some(evaluation) = self.evaluation {
            let config = evaluation.config.unwrap_or_default();
            let tasks: AssertionTasks = AssertionTasks::from_tasks_file(evaluation.tasks);
            let profile =
                GenAIEvalProfile::build_from_parts(config, tasks, Some(evaluation.alias))?;
            card.eval_profile = Some(profile);
        }

        Ok(card)
    }
}

#[derive(Debug, Deserialize)]
pub struct PromptCardInternal {
    pub prompt: Prompt,
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub tags: Vec<String>,
    pub metadata: PromptCardMetadata,
    pub registry_type: RegistryType,
    pub app_env: String,
    pub created_at: DateTime<Utc>,
    pub is_card: bool,
    pub opsml_version: String,
    pub eval_profile: Option<GenAIEvalProfile>,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum PromptCardFormat {
    Full(Box<PromptCardInternal>),
    Generic(Box<PromptConfig>),
}

impl<'de> Deserialize<'de> for PromptCard {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let format = PromptCardFormat::deserialize(deserializer)?;

        match format {
            PromptCardFormat::Generic(config) => {
                debug!("Deserialized PromptCard format: Generic");
                config
                    .into_promptcard()
                    .inspect_err(|e| {
                        error!("Failed to convert PromptConfig to PromptCard: {e}");
                    })
                    .map_err(serde::de::Error::custom)
            }
            PromptCardFormat::Full(internal) => Ok(PromptCard {
                prompt: internal.prompt,
                space: internal.space,
                name: internal.name,
                version: internal.version,
                uid: internal.uid,
                tags: internal.tags,
                metadata: internal.metadata,
                registry_type: internal.registry_type,
                app_env: internal.app_env,
                created_at: internal.created_at,
                is_card: internal.is_card,
                opsml_version: internal.opsml_version,
                eval_profile: internal.eval_profile,
            }),
        }
    }
}

impl PromptCard {
    pub fn new_rs(
        prompt: Prompt,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        eval_profile: Option<GenAIEvalProfile>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Prompt;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)?;

        Ok(Self {
            prompt,
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags: tags.unwrap_or_default(),
            metadata: PromptCardMetadata::default(),
            registry_type,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
            eval_profile,
        })
    }
    /// Save drift profile
    ///
    /// # Arguments
    ///
    /// * `path` - Path to save drift profile
    ///
    /// # Returns
    ///
    /// * `PyResult<PathBuf>` - Path to saved drift profile
    #[instrument(skip_all, name = "save_eval_profile")]
    pub fn save_eval_profile(
        &mut self,
        path: &Path,
    ) -> Result<HashMap<String, DriftProfileUri>, CardError> {
        let profile = self
            .eval_profile
            .as_ref()
            .ok_or(CardError::DriftProfileNotFoundError)?;

        let alias = profile
            .alias
            .clone()
            .unwrap_or_else(|| "eval_profile".to_string());

        let mut drift_url_map = HashMap::new();
        let save_dir = PathBuf::from(SaveName::Evaluation);

        let relative_path = save_dir.join(alias.clone()).with_extension(Suffix::Json);
        let full_path = path.join(&relative_path);

        let drift_type = DriftType::GenAI;
        profile.save_to_json(Some(full_path))?;

        drift_url_map.insert(
            alias,
            DriftProfileUri {
                root_dir: save_dir.clone(),
                uri: relative_path,
                drift_type,
            },
        );
        debug!("Drift profile saved");
        Ok(drift_url_map)
    }

    /// Load drift profile
    ///
    /// # Arguments
    ///
    /// * `path` - Path to load drift profile
    ///
    /// # Returns
    ///
    /// * `PyResult<()>` - Result of loading drift profile
    pub fn load_drift_profile(&mut self, path: &Path) -> Result<(), CardError> {
        let map = self
            .metadata
            .drift_profile_uri_map
            .as_ref()
            .ok_or(CardError::DriftProfileNotFoundInMap)?;

        for (alias, drift_profile_uri) in map {
            debug!(filepath = ?drift_profile_uri.uri, tmp_path = ?path, "Loading drift profile for alias: {}", alias);

            let filepath = path.join(&drift_profile_uri.uri);

            debug!("Drift profile file path: {:?}", filepath);

            // load file to json string
            let file = std::fs::read_to_string(&filepath)?;

            match drift_profile_uri.drift_type {
                DriftType::GenAI => {
                    let profile = GenAIEvalProfile::model_validate_json(file);
                    self.eval_profile = Some(profile);
                }
                _ => {
                    error!(
                        "PromptCard does not support drift type: {:?}",
                        drift_profile_uri.drift_type
                    );
                    return Err(CardError::UnsupportedDriftType(
                        drift_profile_uri.drift_type.clone(),
                    ));
                }
            }
        }

        Ok(())
    }
}
