use crate::error::CardError;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_crypt::decrypt_directory;
use opsml_storage::storage_client;
use opsml_types::cards::{CardStatus, EvalMetrics};
use opsml_types::contracts::{CardRecord, ExperimentCardClientRecord};
use opsml_types::{
    RegistryType, SaveName, Suffix,
    cards::{ComputeEnvironment, Metrics, Parameters},
    contracts::ArtifactKey,
};
use opsml_utils::{PyHelperFuncs, get_utc_datetime};
use pyo3::prelude::*;
use serde_json;
use std::path::PathBuf;
use tracing::error;

use serde::{
    Deserialize, Deserializer, Serialize, Serializer,
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct UidMetadata {
    #[pyo3(get, set)]
    pub datacard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub modelcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub promptcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub service_card_uids: Vec<String>,

    #[pyo3(get, set)]
    pub experimentcard_uids: Vec<String>,
}

#[pyclass]
pub struct ExperimentCard {
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
    pub uids: UidMetadata,

    #[pyo3(get)]
    pub compute_environment: ComputeEnvironment,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get)]
    pub subexperiment: bool,

    #[pyo3(get)]
    pub opsml_version: String,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get, set)]
    eval_metrics: EvalMetrics,

    artifact_key: Option<ArtifactKey>,

    #[pyo3(get, set)]
    status: CardStatus,
}

#[pymethods]
impl ExperimentCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (space=None, name=None, version=None, uid=None, tags=None))]
    pub fn new(
        py: Python,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<Vec<String>>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Experiment;
        let tags = tags.unwrap_or_default();

        let base_args = BaseArgs::create_args(name, space, version, uid, &registry_type)?;

        Ok(Self {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            registry_type,
            artifact_key: None,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            compute_environment: ComputeEnvironment::new(py)?,
            uids: UidMetadata::default(),
            subexperiment: false,
            is_card: true,
            opsml_version: opsml_version::version(),
            eval_metrics: EvalMetrics::default(),
            status: CardStatus::Active,
        })
    }

    #[pyo3(signature = (names = None))]
    pub fn get_parameters(
        &self,
        py: Python,
        names: Option<Vec<String>>,
    ) -> Result<Parameters, CardError> {
        // a little nested import here
        // It would be preferable to use "get_experiment_parameters" from opsml_experiment
        // but opsml_experiment relies on opsml_registry which relies on opsml_cards
        // thus, it would create a circular dependency. We can always revisit this later
        let func = py
            .import("opsml.experiment")?
            .getattr("get_experiment_parameters")?;

        let parameters = func.call1((&self.uid, names))?.extract::<Parameters>()?;

        Ok(parameters)
    }

    #[pyo3(signature = (names = None))]
    pub fn get_metrics(
        &self,
        py: Python,
        names: Option<Vec<String>>,
    ) -> Result<Metrics, CardError> {
        // get the experiment registry
        let func = py
            .import("opsml.experiment")?
            .getattr("get_experiment_metrics")?;

        let memory_metrics = func.call1((&self.uid, names))?.extract::<Metrics>()?;

        Ok(memory_metrics)
    }

    pub fn add_subexperiment_experiment(&mut self, uid: &str) {
        self.uids.experimentcard_uids.push(uid.to_string());
    }

    pub fn add_promptcard_uid(&mut self, uid: &str) {
        self.uids.promptcard_uids.push(uid.to_string());
    }

    pub fn add_datacard_uid(&mut self, uid: &str) {
        self.uids.datacard_uids.push(uid.to_string());
    }

    pub fn add_modelcard_uid(&mut self, uid: &str) {
        self.uids.modelcard_uids.push(uid.to_string());
    }

    pub fn add_service_card_uid(&mut self, uid: &str) {
        self.uids.service_card_uids.push(uid.to_string());
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = ExperimentCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            datacard_uids: self.uids.datacard_uids.clone(),
            modelcard_uids: self.uids.modelcard_uids.clone(),
            promptcard_uids: self.uids.promptcard_uids.clone(),
            service_card_uids: self.uids.service_card_uids.clone(),
            experimentcard_uids: self.uids.experimentcard_uids.clone(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            status: self.status.clone(),
        };

        Ok(CardRecord::Experiment(record))
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> Result<ExperimentCard, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {}", e);
        })?)
    }

    #[pyo3(signature = (path=None))]
    pub fn list_artifacts(&self, path: Option<PathBuf>) -> Result<Vec<String>, CardError> {
        let storage_path = self.artifact_key.as_ref().unwrap().storage_path();

        let rpath = match path {
            None => storage_path.join(SaveName::Artifacts),
            Some(p) => storage_path.join(SaveName::Artifacts).join(p),
        };

        let files = storage_client()?.find(&rpath).inspect_err(|e| {
            error!("Failed to list artifacts: {e}");
        })?;

        // iterate through and remove storage_path if it exists
        let storage_path_str = storage_path.into_os_string().into_string().map_err(|_| {
            error!("Failed to convert storage path to string");
            CardError::IntoStringError
        })?;

        let files = files
            .iter()
            .map(|f| {
                let path = f.strip_prefix(&storage_path_str).unwrap_or(f);
                path.to_string()
            })
            .collect();

        Ok(files)
    }

    #[pyo3(signature = (path=None, lpath=None))]
    pub fn download_artifacts(
        &self,
        path: Option<PathBuf>,
        lpath: Option<PathBuf>,
    ) -> Result<(), CardError> {
        let storage_path = self.artifact_key.as_ref().unwrap().storage_path();

        // if lpath is None, download to "artifacts" directory
        let mut lpath = lpath.unwrap_or_else(|| PathBuf::from("artifacts"));

        // assert that lpath exists, if not create it
        if !lpath.exists() {
            std::fs::create_dir_all(&lpath).inspect_err(|e| {
                error!("Failed to create directory: {e}");
            })?;
        }

        let rpath = if let Some(path) = &path {
            lpath = lpath.join(path);
            storage_path.join(SaveName::Artifacts).join(path)
        } else {
            // download everything to "artifacts" directory
            storage_path.join(SaveName::Artifacts)
        };

        // if rpath has an extension, set recursive to false
        let recursive = rpath.extension().is_none();

        storage_client()?
            .get(&lpath, &rpath, recursive)
            .inspect_err(|e| {
                error!("Failed to download artifacts: {e}");
            })?;

        let decrypt_key = self
            .artifact_key
            .as_ref()
            .unwrap()
            .get_decrypt_key()
            .inspect_err(|e| {
                error!("Failed to get decryption key: {e}");
            })?;
        decrypt_directory(&lpath, &decrypt_key)?;

        Ok(())
    }

    /// Download a specific artifact
    #[pyo3(signature = (path, lpath=None))]
    pub fn download_artifact(
        &self,
        py: Python<'_>,
        path: PathBuf,
        lpath: Option<PathBuf>,
    ) -> Result<(), CardError> {
        // Same as above, we need to use a registry to get the experiment artifact
        // In the future we could consider adding a global registry to app_state if needed,
        // But I prefer not to
        let func = py
            .import("opsml.experiment")?
            .getattr("download_artifact")?;

        func.call1((&self.uid, path, lpath))?;

        Ok(())
    }
}

impl ExperimentCard {
    pub fn set_artifact_key(&mut self, key: ArtifactKey) {
        self.artifact_key = Some(key);
    }
}

impl Serialize for ExperimentCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ExperimentCard", 15)?;

        // set session to none
        state.serialize_field("name", &self.name)?;
        state.serialize_field("space", &self.space)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("tags", &self.tags)?;
        state.serialize_field("registry_type", &self.registry_type)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("app_env", &self.app_env)?;
        state.serialize_field("compute_environment", &self.compute_environment)?;
        state.serialize_field("uids", &self.uids)?;
        state.serialize_field("subexperiment", &self.subexperiment)?;
        state.serialize_field("is_card", &self.is_card)?;
        state.serialize_field("opsml_version", &self.opsml_version)?;
        state.serialize_field("eval_metrics", &self.eval_metrics)?;
        state.serialize_field("status", &self.status)?;
        state.end()
    }
}

impl<'de> Deserialize<'de> for ExperimentCard {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Name,
            Space,
            Version,
            Uid,
            Tags,
            RegistryType,
            AppEnv,
            CreatedAt,
            ComputeEnvironment,
            Uids,
            Subexperiment,
            IsCard,
            OpsmlVersion,
            EvalMetrics,
            Status,
        }

        struct ExperimentCardVisitor;

        impl<'de> Visitor<'de> for ExperimentCardVisitor {
            type Value = ExperimentCard;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ExperimentCard")
            }

            fn visit_map<V>(self, mut map: V) -> Result<ExperimentCard, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut name = None;
                let mut space = None;
                let mut version = None;
                let mut uid = None;
                let mut tags = None;
                let mut registry_type = None;
                let mut app_env = None;
                let mut created_at = None;
                let mut compute_environment = None;
                let mut uids = None;
                let mut subexperiment = None;
                let mut is_card = None;
                let mut opsml_version = None;
                let mut eval_metrics = None;
                let mut status = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Space => {
                            space = Some(map.next_value()?);
                        }

                        Field::Version => {
                            version = Some(map.next_value()?);
                        }
                        Field::Uid => {
                            uid = Some(map.next_value()?);
                        }
                        Field::Tags => {
                            tags = Some(map.next_value()?);
                        }

                        Field::RegistryType => {
                            registry_type = Some(map.next_value()?);
                        }
                        Field::AppEnv => {
                            app_env = Some(map.next_value()?);
                        }
                        Field::CreatedAt => {
                            created_at = Some(map.next_value()?);
                        }
                        Field::ComputeEnvironment => {
                            compute_environment = Some(map.next_value()?);
                        }
                        Field::Uids => {
                            uids = Some(map.next_value()?);
                        }

                        Field::Subexperiment => {
                            subexperiment = Some(map.next_value()?);
                        }
                        Field::IsCard => {
                            is_card = Some(map.next_value()?);
                        }
                        Field::OpsmlVersion => {
                            opsml_version = Some(map.next_value()?);
                        }
                        Field::EvalMetrics => {
                            eval_metrics = Some(map.next_value()?);
                        }
                        Field::Status => {
                            status = Some(map.next_value()?);
                        }
                    }
                }

                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let space = space.ok_or_else(|| de::Error::missing_field("space"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let tags = tags.ok_or_else(|| de::Error::missing_field("tags"))?;
                let registry_type =
                    registry_type.ok_or_else(|| de::Error::missing_field("registry_type"))?;
                let app_env = app_env.ok_or_else(|| de::Error::missing_field("app_env"))?;
                let created_at =
                    created_at.ok_or_else(|| de::Error::missing_field("created_at"))?;
                let compute_environment = compute_environment
                    .ok_or_else(|| de::Error::missing_field("compute_environment"))?;
                let uids = uids.ok_or_else(|| de::Error::missing_field("uids"))?;

                let subexperiment =
                    subexperiment.ok_or_else(|| de::Error::missing_field("subexperiment"))?;
                let is_card = is_card.ok_or_else(|| de::Error::missing_field("is_card"))?;
                let opsml_version =
                    opsml_version.ok_or_else(|| de::Error::missing_field("opsml_version"))?;
                let eval_metrics =
                    eval_metrics.ok_or_else(|| de::Error::missing_field("eval_metrics"))?;
                let status = status.ok_or_else(|| de::Error::missing_field("status"))?;

                Ok(ExperimentCard {
                    name,
                    space,
                    version,
                    uid,
                    tags,
                    registry_type,
                    artifact_key: None,
                    app_env,
                    created_at,
                    compute_environment,
                    uids,
                    subexperiment,
                    is_card,
                    opsml_version,
                    eval_metrics,
                    status,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "name",
            "space",
            "version",
            "uid",
            "tags",
            "metadata",
            "registry_type",
            "app_env",
            "created_at",
            "compute_environment",
            "uids",
            "subexperiment",
            "is_card",
            "opsml_version",
            "eval_metrics",
            "status",
        ];
        deserializer.deserialize_struct("ExperimentCard", FIELDS, ExperimentCardVisitor)
    }
}

impl FromPyObject<'_, '_> for ExperimentCard {
    type Error = PyErr;
    fn extract(ob: Borrowed<'_, '_, PyAny>) -> PyResult<Self> {
        let space = ob.getattr("space")?.extract()?;
        let name = ob.getattr("name")?.extract()?;
        let version = ob.getattr("version")?.extract()?;
        let uid = ob.getattr("uid")?.extract()?;
        let tags = ob.getattr("tags")?.extract()?;
        let uids = ob.getattr("uids")?.extract()?;
        let compute_environment = ob.getattr("compute_environment")?.extract()?;
        let registry_type = RegistryType::Experiment;
        let app_env = ob.getattr("app_env")?.extract()?;
        let created_at = ob.getattr("created_at")?.extract()?;
        let subexperiment = ob.getattr("subexperiment")?.extract()?;
        let artifact_key = None;
        let opsml_version = ob.getattr("opsml_version")?.extract()?;
        let eval_metrics = ob.getattr("eval_metrics")?.extract()?;
        let status = ob.getattr("status")?.extract()?;

        Ok(ExperimentCard {
            space,
            name,
            version,
            uid,
            tags,
            uids,
            compute_environment,
            registry_type,
            app_env,
            created_at,
            subexperiment,
            artifact_key,
            is_card: true,
            opsml_version,
            eval_metrics,
            status,
        })
    }
}
