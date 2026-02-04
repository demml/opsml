use crate::error::CardError;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_interfaces::base::utils;
use opsml_interfaces::DriftProfileMap;
use opsml_types::contracts::{CardRecord, PromptCardClientRecord};
use opsml_types::DriftProfileUri;
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use potato_head::prompt_types::Prompt;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyList;
use pyo3::IntoPyObjectExt;
use scouter_client::PyDrifter;
use scouter_client::{DriftType, GenAIEvalConfig, GenAIEvalProfile};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument};

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
#[derive(Debug, Serialize, Deserialize, Clone)]
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

    pub eval_profile: DriftProfileMap,
}

#[pymethods]
impl PromptCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (prompt, space=None, name=None, version=None, uid=None, tags=None, eval_profile=None))]
    pub fn new(
        prompt: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
        eval_profile: Option<&Bound<'_, PyAny>>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Prompt;
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t.extract::<Vec<String>>()?,
        };

        let base_args = BaseArgs::create_args(name, space, version, uid, &registry_type)?;

        let prompt = prompt.extract::<Prompt>().inspect_err(|e| {
            error!("Failed to extract prompt: {e}");
        })?;

        let profiles = match eval_profile {
            Some(profile) => utils::extract_drift_profile(profile)?,
            None => DriftProfileMap::new(),
        };

        Ok(Self {
            prompt,
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            metadata: PromptCardMetadata::default(),
            registry_type,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
            eval_profile: profiles,
        })
    }

    #[getter]
    pub fn eval_profile<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, DriftProfileMap>, CardError> {
        let pyob = Py::new(py, self.eval_profile.clone())?;
        let bound = pyob.bind(py).clone();
        Ok(bound)
    }

    #[setter]
    pub fn set_eval_profile(
        &mut self,
        eval_profile: Bound<'_, DriftProfileMap>,
    ) -> Result<(), CardError> {
        self.eval_profile = eval_profile.extract().inspect_err(|e| {
            error!("Failed to extract eval profile: {e}");
        })?;

        Ok(())
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
    pub fn save(&mut self, py: Python, path: PathBuf) -> Result<(), CardError> {
        debug!("Saving PromptCard to path: {:?}", path);

        // save eval profile
        let eval_profile_uri_map = if self.eval_profile.is_empty() {
            None
        } else {
            Some(self.save_eval_profile(py, &path)?)
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
        py: Python<'_>,
        alias: String,
        tasks: &Bound<'_, PyList>,
        config: Option<GenAIEvalConfig>,
    ) -> Result<(), CardError> {
        debug!("Creating eval profile");

        let mut drifter = PyDrifter::new();
        let profile = drifter.create_genai_drift_profile(py, tasks, config, Some(alias.clone()))?;
        self.eval_profile.add_profile(py, alias, profile.clone())?;
        Ok(())
    }

    #[pyo3(name = "_update_drift_config_args")]
    fn update_drift_config_args(&mut self, py: Python) -> Result<(), CardError> {
        // if eval_profiles is empty, return
        if self.eval_profile.is_empty() {
            Ok(())
        } else {
            // set new config args from card and update all profiles
            let config_args = PyDict::new(py);
            config_args.set_item("name", &self.name)?;
            config_args.set_item("space", &self.space)?;
            config_args.set_item("version", &self.version)?;

            self.eval_profile.update_config_args(py, &config_args)?;

            Ok(())
        }
    }
}

impl PromptCard {
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
        py: Python,
        path: &Path,
    ) -> Result<HashMap<String, DriftProfileUri>, CardError> {
        let mut drift_url_map = HashMap::new();
        let save_dir = PathBuf::from(SaveName::Drift);

        for (alias, profile) in self.eval_profile.profiles.iter() {
            let relative_path = save_dir.join(alias).with_extension(Suffix::Json);
            let full_path = path.join(&relative_path);

            let drift_type = DriftType::GenAI;
            profile.call_method1(py, "save_to_json", (Some(&full_path),))?;

            drift_url_map.insert(
                alias.to_string(),
                DriftProfileUri {
                    root_dir: save_dir.clone(),
                    uri: relative_path,
                    drift_type,
                },
            );
        }
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
    pub fn load_drift_profile(&mut self, py: Python, path: &Path) -> Result<(), CardError> {
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
                    self.eval_profile.add_profile(
                        py,
                        alias.to_string(),
                        profile.into_bound_py_any(py)?,
                    )?;
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
