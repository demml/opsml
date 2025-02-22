use chrono::NaiveDateTime;
use opsml_crypt::decrypt_directory;
use opsml_error::{CardError, OpsmlError};
use opsml_storage::FileSystemStorage;
use opsml_types::contracts::{Card, ExperimentCardClientRecord};
use opsml_types::{
    cards::{BaseArgs, ComputeEnvironment},
    contracts::ArtifactKey,
    RegistryType, SaveName, Suffix,
};
use opsml_utils::{get_utc_datetime, PyHelperFuncs};
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde_json;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::error;

use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};

#[pyclass]
pub struct ExperimentCard {
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
    pub datacard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub modelcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub experimentcard_uids: Vec<String>,

    #[pyo3(get)]
    pub compute_environment: ComputeEnvironment,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: NaiveDateTime,

    #[pyo3(get)]
    pub subexperiment: bool,

    pub rt: Option<Arc<tokio::runtime::Runtime>>,

    pub fs: Option<Arc<Mutex<FileSystemStorage>>>,

    pub artifact_key: Option<ArtifactKey>,
}

#[pymethods]
impl ExperimentCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (repository=None, name=None, version=None, uid=None, tags=None))]
    pub fn new(
        py: Python,
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

        Ok(Self {
            repository: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            registry_type: RegistryType::Experiment,
            rt: None,
            fs: None,
            artifact_key: None,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            compute_environment: ComputeEnvironment::new(py)?,
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            experimentcard_uids: Vec::new(),
            subexperiment: false,
        })
    }

    pub fn add_subexperiment_experiment(&mut self, uid: &str) {
        self.experimentcard_uids.push(uid.to_string());
    }

    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        let record = ExperimentCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            repository: self.repository.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            datacard_uids: self.datacard_uids.clone(),
            modelcard_uids: self.modelcard_uids.clone(),
            experimentcard_uids: self.experimentcard_uids.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(Card::Experiment(record))
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> PyResult<ExperimentCard> {
        serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            OpsmlError::new_err(e.to_string())
        })
    }

    #[pyo3(signature = (path=None))]
    pub fn list_artifacts(&self, path: Option<PathBuf>) -> PyResult<Vec<String>> {
        let rt = self.rt.as_ref().unwrap();
        let fs = self.fs.as_ref().unwrap();
        let storage_path = self.artifact_key.as_ref().unwrap().storage_path();

        let rpath = if path.is_none() {
            storage_path.join(SaveName::Artifacts)
        } else {
            storage_path.join(SaveName::Artifacts).join(path.unwrap())
        };

        let files = rt
            .block_on(async {
                let mut storage = fs.lock().await;
                storage.find(&rpath).await
            })
            .map_err(|e| {
                error!("Failed to list artifacts: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        // iterate through and remove storage_path if it exists
        let storage_path_str = storage_path
            .into_os_string()
            .into_string()
            .map_err(|e| OpsmlError::new_err(e))?;

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
    ) -> PyResult<()> {
        let rt = self.rt.as_ref().unwrap();
        let fs = self.fs.as_ref().unwrap();
        let storage_path = self.artifact_key.as_ref().unwrap().storage_path();

        // if lpath is None, download to "artifacts" directory
        let mut lpath = lpath.unwrap_or_else(|| PathBuf::from("artifacts"));

        // assert that lpath exists, if not create it
        if !lpath.exists() {
            std::fs::create_dir_all(&lpath).map_err(|e| {
                error!("Failed to create directory: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;
        }

        let rpath = if path.is_none() {
            // download everything to "artifacts" directory
            storage_path.join(SaveName::Artifacts)
        } else {
            lpath = lpath.join(path.as_ref().unwrap());
            storage_path
                .join(SaveName::Artifacts)
                .join(path.as_ref().unwrap())
        };

        // if rpath has an extension, set recursive to false
        let recursive = rpath.extension().is_none();

        rt.block_on(async {
            let mut storage = fs.lock().await;
            storage.get(&lpath, &rpath, recursive).await
        })
        .map_err(|e| {
            error!("Failed to download artifacts: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;

        let decrypt_key = self
            .artifact_key
            .as_ref()
            .unwrap()
            .get_decrypt_key()
            .map_err(|e| {
                error!("Failed to get decryption key: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;
        decrypt_directory(&lpath, &decrypt_key)?;

        Ok(())
    }
}

impl Serialize for ExperimentCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ExperimentCard", 13)?;

        // set session to none
        state.serialize_field("name", &self.name)?;
        state.serialize_field("repository", &self.repository)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("tags", &self.tags)?;
        state.serialize_field("registry_type", &self.registry_type)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("app_env", &self.app_env)?;
        state.serialize_field("compute_environment", &self.compute_environment)?;
        state.serialize_field("datacard_uids", &self.datacard_uids)?;
        state.serialize_field("modelcard_uids", &self.modelcard_uids)?;
        state.serialize_field("experimentcard_uids", &self.experimentcard_uids)?;
        state.serialize_field("subexperiment", &self.subexperiment)?;
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
            Repository,
            Version,
            Uid,
            Tags,
            RegistryType,
            AppEnv,
            CreatedAt,
            ComputeEnvironment,
            DatacardUids,
            ModelcardUids,
            ExperimentcardUids,
            Subexperiment,
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
                let mut repository = None;
                let mut version = None;
                let mut uid = None;
                let mut tags = None;
                let mut registry_type = None;
                let mut app_env = None;
                let mut created_at = None;
                let mut compute_environment = None;
                let mut datacard_uids = None;
                let mut modelcard_uids = None;
                let mut experimentcard_uids = None;
                let mut subexperiment = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Repository => {
                            repository = Some(map.next_value()?);
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
                        Field::DatacardUids => {
                            datacard_uids = Some(map.next_value()?);
                        }
                        Field::ModelcardUids => {
                            modelcard_uids = Some(map.next_value()?);
                        }
                        Field::ExperimentcardUids => {
                            experimentcard_uids = Some(map.next_value()?);
                        }
                        Field::Subexperiment => {
                            subexperiment = Some(map.next_value()?);
                        }
                    }
                }

                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let repository =
                    repository.ok_or_else(|| de::Error::missing_field("repository"))?;
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
                let datacard_uids =
                    datacard_uids.ok_or_else(|| de::Error::missing_field("datacard_uids"))?;
                let modelcard_uids =
                    modelcard_uids.ok_or_else(|| de::Error::missing_field("modelcard_uids"))?;
                let experimentcard_uids = experimentcard_uids
                    .ok_or_else(|| de::Error::missing_field("experimentcard_uids"))?;
                let subexperiment =
                    subexperiment.ok_or_else(|| de::Error::missing_field("subexperiment"))?;

                Ok(ExperimentCard {
                    name,
                    repository,
                    version,
                    uid,
                    tags,
                    registry_type,
                    rt: None,
                    fs: None,
                    artifact_key: None,
                    app_env,
                    created_at,
                    compute_environment,
                    datacard_uids,
                    modelcard_uids,
                    experimentcard_uids,
                    subexperiment,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "name",
            "repository",
            "version",
            "uid",
            "tags",
            "metadata",
            "registry_type",
            "app_env",
            "created_at",
            "compute_environment",
            "datacard_uids",
            "modelcard_uids",
            "experimentcard_uids",
            "subexperiment",
        ];
        deserializer.deserialize_struct("ExperimentCard", FIELDS, ExperimentCardVisitor)
    }
}

impl FromPyObject<'_> for ExperimentCard {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let repository = ob.getattr("repository")?.extract()?;
        let name = ob.getattr("name")?.extract()?;
        let version = ob.getattr("version")?.extract()?;
        let uid = ob.getattr("uid")?.extract()?;
        let tags = ob.getattr("tags")?.extract()?;
        let datacard_uids = ob.getattr("datacard_uids")?.extract()?;
        let modelcard_uids = ob.getattr("modelcard_uids")?.extract()?;
        let experimentcard_uids = ob.getattr("experimentcard_uids")?.extract()?;
        let compute_environment = ob.getattr("compute_environment")?.extract()?;
        let registry_type = RegistryType::Experiment;
        let app_env = ob.getattr("app_env")?.extract()?;
        let created_at = ob.getattr("created_at")?.extract()?;
        let subexperiment = ob.getattr("subexperiment")?.extract()?;
        let rt = None;
        let fs = None;
        let artifact_key = None;

        Ok(ExperimentCard {
            repository,
            name,
            version,
            uid,
            tags,
            datacard_uids,
            modelcard_uids,
            experimentcard_uids,
            compute_environment,
            registry_type,
            app_env,
            created_at,
            subexperiment,
            rt,
            fs,
            artifact_key,
        })
    }
}
