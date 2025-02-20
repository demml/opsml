use crate::ActiveRun;
use crate::ComputeEnvironment;
use chrono::NaiveDateTime;
use names::Generator;
use opsml_error::OpsmlError;
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use opsml_storage::FileSystemStorage;
use opsml_types::{cards::BaseArgs, contracts::ArtifactKey, RegistryType};
use opsml_utils::get_utc_datetime;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::IntoPyObjectExt;
use std::sync::{Arc, Mutex};
use tracing::error;

#[pyclass]
pub struct RunCard {
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
    pub runcard_uids: Vec<String>,

    #[pyo3(get, set)]
    pub artifacts: Vec<String>,

    #[pyo3(get)]
    pub compute_environment: ComputeEnvironment,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: NaiveDateTime,

    pub rt: Option<Arc<tokio::runtime::Runtime>>,

    pub fs: Option<Arc<Mutex<FileSystemStorage>>>,

    pub artifact_key: Option<ArtifactKey>,
}

#[pymethods]
impl RunCard {
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
        let name = name.map(String::from).unwrap_or_else(|| {
            let mut generator = Generator::default();
            generator.next().unwrap_or_else(|| "run".to_string())
        });

        let tags = match tags {
            None => Vec::new(),
            Some(t) => t
                .extract::<Vec<String>>()
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
        };

        let base_args =
            BaseArgs::create_args(Some(&name), repository, version, uid).map_err(|e| {
                error!("Failed to create base args: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        Ok(Self {
            repository: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            registry_type: RegistryType::Run,
            rt: None,
            fs: None,
            artifact_key: None,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            compute_environment: ComputeEnvironment::new(py)?,
            datacard_uids: Vec::new(),
            modelcard_uids: Vec::new(),
            runcard_uids: Vec::new(),
            artifacts: Vec::new(),
        })
    }

    pub fn add_child_run(&mut self, uid: &str) {
        self.runcard_uids.push(uid.to_string());
    }

    #[staticmethod]
    #[pyo3(signature = (repository=None, name=None, code_dir=None, log_hardware=false))]
    pub fn start_run<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        code_dir: Option<&str>,
        log_hardware: bool,
    ) -> PyResult<Bound<'py, ActiveRun>> {
        let run = Py::new(py, RunCard::new(py, repository, name, None, None, None)?)?
            .into_bound_py_any(py)
            .map_err(|e| {
                error!("Failed to register run card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let mut registries = CardRegistries::new()?;
        registries
            .run
            .register_card(&run, VersionType::Minor, None, None, None)?;

        let _hardware = log_hardware;
        let _code_dir = code_dir.unwrap_or("");

        // Return the new ActiveRun wrapped in a PyRef which implements context manager protocol
        let active = ActiveRun::new(run.unbind(), Arc::new(Mutex::new(registries)))?;

        Ok(Py::new(py, active)?.bind(py).clone())
    }
}

//run_name: str | None = None,
//log_hardware: bool = False,
//hardware_interval: int = _DEFAULT_INTERVAL,
//code_dir: str | Path | None = None
