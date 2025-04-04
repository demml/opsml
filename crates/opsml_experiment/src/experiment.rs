use crate::HardwareQueue;
use chrono::{DateTime, Utc};
use names::Generator;
use opsml_cards::ExperimentCard;
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::{ExperimentError, OpsmlError};
use opsml_registry::base::OpsmlRegistry;
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use opsml_storage::storage_client;
use opsml_types::cards::{Metrics, Parameters};
use opsml_types::contracts::{
    ArtifactKey, GetMetricRequest, GetParameterRequest, MetricRequest, ParameterRequest,
};
use opsml_types::RegistryType;
use opsml_types::{
    cards::experiment::{Metric, Parameter},
    SaveName,
};
use pyo3::{prelude::*, IntoPyObjectExt};
use std::path::PathBuf;
use std::sync::Arc;
use tracing::{debug, error, instrument, warn};

/// Get the filename of the python file
///
/// # Arguments
///
/// * `py` - The python interpreter
///
/// # Returns
///
/// * `PathBuf` - The path to the python file
///
/// # Errors
///
/// * `ExperimentError` - Error getting the python filename
fn get_py_filename(py: Python) -> Result<PathBuf, ExperimentError> {
    let inspect = py.import("inspect")?;
    let current_frame = inspect.call_method0("currentframe")?;
    let f_code = current_frame.getattr("f_code")?;
    let filename = f_code.getattr("co_filename")?;

    Ok(PathBuf::from(filename.to_string()))
}

/// Extract the code related to the experiment
///
/// # Arguments
///
/// * `py` - The python interpreter
/// * `code_dir` - The directory containing the code
/// * `uid` - The experiment UID
/// * `fs` - The file system storage
/// * `registries` - The registries
/// * `rt` - The tokio runtime
///
/// # Returns
///
/// * `None`
///
/// # Errors
///
/// * `ExperimentError` - Error extracting the code
fn extract_code(
    py: Python<'_>,
    code_dir: Option<PathBuf>,
    artifact_key: &ArtifactKey,
) -> Result<(), ExperimentError> {
    // Attempt to get file
    let (lpath, recursive) = match code_dir {
        Some(path) => (path.to_path_buf(), true),
        None => (get_py_filename(py)?, false),
    };

    // 2. Set rpath based on file or directory
    let rpath = if lpath.is_file() {
        &artifact_key
            .storage_path()
            .join(SaveName::Artifacts)
            .join(SaveName::Code)
            .join(lpath.file_name().unwrap())
    } else {
        &artifact_key
            .storage_path()
            .join(SaveName::Artifacts)
            .join(SaveName::Code)
    };

    let encryption_key = artifact_key.get_decrypt_key()?;

    // 3. Encrypt the file or directory
    encrypt_directory(&lpath, &encryption_key)?;

    storage_client()?.put(&lpath, rpath, recursive)?;

    // 5. Decrypt the file or directory (this is done to ensure the file is not encrypted in the code directory)
    decrypt_directory(&lpath, &encryption_key)?;

    Ok(())
}

#[pyclass]
pub struct Experiment {
    pub experiment: PyObject,
    pub registries: CardRegistries,
    pub hardware_queue: Option<HardwareQueue>,
    uid: String,
    artifact_key: ArtifactKey,
}

impl Experiment {
    #[allow(clippy::too_many_arguments)]
    #[instrument(skip_all)]
    pub fn new(
        py: Python,
        experiment: PyObject,
        registries: CardRegistries,
        log_hardware: bool,
        code_dir: Option<PathBuf>,
        experiment_uid: String,
    ) -> PyResult<Self> {
        // need artifact key for encryption/decryption

        let experiment_registry = &registries.experiment.registry;

        let artifact_key =
            experiment_registry.get_artifact_key(&experiment_uid, &RegistryType::Experiment)?;

        // extract card into ExperimentCard for adding needed fields for use outside of experiment
        // a little but of overhead here, but it's necessary
        // the card must be usable after the experiment is finished (downloading artifacts, etc.)
        let mut experiment: ExperimentCard = experiment.extract(py)?;
        experiment.artifact_key = Some(artifact_key.clone());

        // extract code
        match extract_code(py, code_dir, &artifact_key) {
            Ok(_) => debug!("Code extracted successfully"),
            Err(e) => warn!("Failed to extract code: {}", e),
        };

        // start hardware queue if log_hardware is true
        let hardware_queue = match log_hardware {
            true => {
                // clone the experiment registry
                let registry = registries.experiment.registry.clone();
                let arc_reg = Arc::new(registry);
                let hardware_queue = HardwareQueue::start(arc_reg, experiment_uid.clone())?;
                Some(hardware_queue)
            }

            false => None,
        };

        Ok(Self {
            experiment: experiment.into_py_any(py).map_err(|e| {
                error!("Failed to bind experiment card: {}", e);
                ExperimentError::Error(e.to_string())
            })?,
            registries,
            hardware_queue,
            uid: experiment_uid,
            artifact_key,
        })
    }

    /// Create an experiment
    ///
    /// # Arguments
    ///
    /// * `py` - The python interpreter
    /// * `space` - The space URL
    /// * `name` - The name of the experiment
    /// * `code_dir` - The directory containing the code
    /// * `registries` - The registries
    /// * `subexperiment` - Whether the experiment is a subexperiment
    /// * `fs` - The file system storage
    /// * `rt` - The tokio runtime
    ///
    /// # Returns
    ///
    /// * `Bound<PyAny>` - The experiment card
    /// * `String` - The experiment UID
    ///
    /// # Errors
    ///
    /// * `ExperimentError` - Error creating the experiment
    #[instrument(skip_all)]
    fn create_experiment<'py>(
        py: Python<'py>,
        space: Option<&str>,
        name: Option<&str>,
        registries: &mut CardRegistries,
        subexperiment: bool,
    ) -> PyResult<(Bound<'py, PyAny>, String)> {
        let name = name.map(String::from).unwrap_or_else(|| {
            let mut generator = Generator::default();
            generator.next().unwrap_or_else(|| "experiment".to_string())
        });

        debug!("Initializing experiment");
        let experiment = Self::initialize_experiment(py, space, Some(&name), subexperiment)?;

        debug!("Registering experiment");
        let uid = Self::register_experiment(&experiment, registries)?;

        Ok((experiment, uid))
    }

    /// Initialize the experiment
    ///
    /// # Arguments
    ///
    /// * `py` - The python interpreter
    /// * `space` - The space URL
    /// * `name` - The name of the experiment
    /// * `subexperiment` - Whether the experiment is a subexperiment
    ///
    /// # Returns
    ///
    /// * `Bound<PyAny>` - The experiment card
    ///
    /// # Errors
    ///
    /// * `ExperimentError` - Error initializing the experiment
    fn initialize_experiment<'py>(
        py: Python<'py>,
        space: Option<&str>,
        name: Option<&str>,
        subexperiment: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let mut card = ExperimentCard::new(py, space, name, None, None, None)?;
        card.subexperiment = subexperiment;

        let experiment = Py::new(py, card)?.into_bound_py_any(py).map_err(|e| {
            error!("Failed to register experiment card: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(experiment)
    }

    /// Register the experiment
    ///
    /// # Arguments
    ///
    /// * `experiment` - The experiment
    /// * `registries` - The registries
    /// * `code_dir` - The directory containing the code
    /// * `fs` - The file system storage
    /// * `rt` - The tokio runtime
    ///
    /// # Returns
    ///
    /// * `String` - The experiment UID
    ///
    /// # Errors
    ///
    /// * `OpsmlError` - Error registering the experiment
    #[instrument(skip_all)]
    fn register_experiment(
        experiment: &Bound<'_, PyAny>,
        registries: &mut CardRegistries,
    ) -> PyResult<String> {
        registries
            .experiment
            .register_card(experiment, VersionType::Minor, None, None, None)
            .map_err(|e| {
                error!("Failed to register experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let uid = experiment.getattr("uid")?.extract::<String>()?;

        Ok(uid)
    }

    /// Add a subexperiment to the experiment
    ///
    /// # Arguments
    ///
    /// * `subexperiment` - The subexperiment
    ///
    /// # Returns
    ///
    /// * `None`
    ///
    /// # Errors
    ///
    /// * `OpsmlError` - Error adding the subexperiment
    fn add_subexperiment_experiment<'py>(
        slf: &PyRefMut<'py, Self>,
        py: Python<'py>,
        subexperiment: &Experiment,
    ) -> PyResult<()> {
        let subexperiment_uid = subexperiment.uid.clone();
        slf.experiment
            .call_method1(py, "add_subexperiment_experiment", (&subexperiment_uid,))?;
        Ok(())
    }

    /// Load an existing experiment
    ///
    /// # Arguments
    ///
    /// * `experiment_uid` - The experiment UID
    ///
    /// # Returns
    ///
    /// * `Bound<Experiment>` - The experiment
    ///
    /// # Errors
    ///
    /// * `OpsmlError` - Error loading the experiment
    #[instrument(skip_all)]
    fn load_experiment<'py>(
        py: Python<'py>,
        experiment_uid: &str,
        registries: &mut CardRegistries,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Logic to load the existing experiment using the experiment_id
        let experiment = registries
            .experiment
            .load_card(py, Some(experiment_uid.to_string()), None, None, None, None)
            .map_err(|e| {
                error!("Failed to load experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?
            .into_bound_py_any(py)
            .map_err(|e| {
                error!("Failed to bind experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        Ok(experiment)
    }

    fn stop_queue(&mut self) -> Result<(), ExperimentError> {
        if let Some(mut queue) = self.hardware_queue.take() {
            queue.stop();
        }
        Ok(())
    }
}

#[pymethods]
impl Experiment {
    /// Start a child experiment
    ///
    /// # Arguments
    ///
    /// * `space` - The space URL
    /// * `name` - The name of the experiment
    /// * `code_dir` - The directory containing the code
    /// * `log_hardware` - Whether to log hardware metrics. Will log hardware metrics every 30 seconds
    /// * `experiment_uid` - The experiment UID
    ///
    /// # Returns
    ///
    /// * `Bound<Experiment>` - The experiment
    ///
    /// # Errors
    ///
    /// * `ExperimentError` - Error starting the experiment
    #[pyo3(signature = (space=None, name=None, code_dir=None, log_hardware=false, experiment_uid=None))]
    #[instrument(skip_all)]
    pub fn start_experiment<'py>(
        mut slf: PyRefMut<'py, Self>,
        py: Python<'py>,
        space: Option<&str>,
        name: Option<&str>,
        code_dir: Option<PathBuf>,
        log_hardware: bool,
        experiment_uid: Option<&str>,
    ) -> PyResult<Bound<'py, Experiment>> {
        debug!("Starting experiment");
        let registries = &mut slf.registries;
        let experiment = match experiment_uid {
            Some(uid) => {
                let card = Experiment::load_experiment(py, uid, registries)?;
                Experiment::new(
                    py,
                    card.unbind(),
                    slf.registries.clone(),
                    false,
                    code_dir, // we can always revisit, but it doesn't make sense to log hardware for a completed experiment
                    uid.to_string(),
                )?
            }
            None => {
                let (card, uid) = Experiment::create_experiment(py, space, name, registries, true)?;

                Experiment::new(
                    py,
                    card.unbind(),
                    slf.registries.clone(),
                    log_hardware,
                    code_dir,
                    uid,
                )?
            }
        };

        // Add the new experiment's UID to the parent experiment's experimentcard_uids
        debug!("Adding subexperiment to experiment");
        Self::add_subexperiment_experiment(&slf, py, &experiment)?;

        debug!("Starting experiment");

        Ok(Py::new(py, experiment)?.bind(py).clone())
    }

    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        debug!("Starting experiment");
        Ok(slf)
    }

    #[pyo3(signature = (exc_type=None, exc_value=None, traceback=None))]
    fn __exit__(
        mut slf: PyRefMut<'_, Self>,
        py: Python<'_>,
        exc_type: Option<PyObject>,
        exc_value: Option<PyObject>,
        traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        if let (Some(exc_type), Some(exc_value), Some(traceback)) = (exc_type, exc_value, traceback)
        {
            error!(
                "An error occurred: {:?}, {:?}, {:?}",
                exc_type, exc_value, traceback
            );
        } else {
            debug!("Exiting experiment");

            // Bind experiment first to avoid multiple borrows
            let experiment = slf.experiment.clone_ref(py);
            let exp = experiment.bind(py);

            // Update experiment card using the cloned reference
            slf.registries.experiment.update_card(exp)?;

            debug!("Stopping hardware queue");
            slf.stop_queue()?;

            debug!("Experiment updated");
        }
        Ok(false) // Return false to propagate exceptions
    }

    #[pyo3(signature = (name, value, step = None, timestamp = None, created_at = None))]
    pub fn log_metric(
        &self,
        name: String,
        value: f64,
        step: Option<i32>,
        timestamp: Option<i64>,
        created_at: Option<DateTime<Utc>>,
    ) -> PyResult<()> {
        let registry = &self.registries.experiment.registry;

        let metric_request = MetricRequest {
            experiment_uid: self.uid.clone(),
            metrics: vec![Metric {
                name,
                value,
                step,
                timestamp,
                created_at,
            }],
        };

        registry.insert_metrics(&metric_request).map_err(|e| {
            error!("Failed to insert metric: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(())
    }

    pub fn log_metrics(&self, metrics: Vec<Metric>) -> PyResult<()> {
        let registry = &self.registries.experiment.registry;

        let metric_request = MetricRequest {
            experiment_uid: self.uid.clone(),
            metrics,
        };

        registry.insert_metrics(&metric_request).map_err(|e| {
            error!("Failed to insert metric: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(())
    }

    #[pyo3(signature = (name, value))]
    pub fn log_parameter(&self, name: String, value: Bound<'_, PyAny>) -> PyResult<()> {
        let registry = &self.registries.experiment.registry;

        let param_request = ParameterRequest {
            experiment_uid: self.uid.clone(),
            parameters: vec![Parameter::new(name, value)?],
        };

        registry.insert_parameters(&param_request).map_err(|e| {
            error!("Failed to insert metric: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(())
    }

    pub fn log_parameters(&self, parameters: Vec<Parameter>) -> PyResult<()> {
        let registry = &self.registries.experiment.registry;

        let param_request = ParameterRequest {
            experiment_uid: self.uid.clone(),
            parameters,
        };

        registry.insert_parameters(&param_request).map_err(|e| {
            error!("Failed to insert metric: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(())
    }

    pub fn log_artifact(&self, path: PathBuf) -> PyResult<()> {
        // get current working directory
        let cwd = std::env::current_dir().map_err(|e| {
            error!("Failed to get current working directory: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        // check that path exists
        if !path.exists() {
            return Err(OpsmlError::new_err("Path does not exist".to_string()));
        }

        // check that path is a file
        if !path.is_file() {
            return Err(OpsmlError::new_err(
                "Path is not a file. Use log_artifacts if you wish to log multiple artifacts "
                    .to_string(),
            ));
        }

        // get relative path
        let relative_path = if path.is_absolute() {
            path.strip_prefix(&cwd).unwrap_or(&path)
        } else {
            path.as_path()
        };

        let rpath = self
            .artifact_key
            .storage_path()
            .join(SaveName::Artifacts)
            .join(relative_path);

        let encryption_key = self.artifact_key.get_decrypt_key()?;
        encrypt_directory(&path, &encryption_key)?;

        storage_client()?.put(&path, &rpath, false)?;

        decrypt_directory(&path, &encryption_key)?;

        Ok(())
    }

    fn log_artifacts(&self, path: PathBuf) -> PyResult<()> {
        let encryption_key = self.artifact_key.get_decrypt_key()?;
        encrypt_directory(&path, &encryption_key)?;

        let rpath = self.artifact_key.storage_path().join(SaveName::Artifacts);

        storage_client()?.put(&path, &rpath, true)?;

        decrypt_directory(&path, &encryption_key)?;

        Ok(())
    }

    #[getter]
    pub fn card<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        Ok(self.experiment.bind(py).clone())
    }

    #[pyo3(signature = (card, version_type = VersionType::Minor, pre_tag = None, build_tag = None, save_kwargs = None))]
    pub fn register_card(
        &mut self,
        card: &Bound<'_, PyAny>,
        version_type: VersionType,
        pre_tag: Option<String>,
        build_tag: Option<String>,
        save_kwargs: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let py = card.py();
        // get registry type of card
        let registry_type = card.getattr("registry_type")?.extract::<RegistryType>()?;

        // set exerimentcard_uid on card
        match card.setattr("experimentcard_uid", self.uid.clone()) {
            Ok(_) => debug!("Set experimentcard_uid on card"),
            Err(e) => warn!("Failed to set experimentcard_uid on card: {}", e),
        };

        match registry_type {
            RegistryType::Data => {
                self.registries.data.register_card(
                    card,
                    version_type,
                    pre_tag,
                    build_tag,
                    save_kwargs,
                )?;

                // update experimentcard_uids on experiment card
                let datacard_uid = &card.getattr("uid")?.extract::<String>()?;
                self.experiment
                    .bind(py)
                    .call_method1("add_datacard_uid", (datacard_uid,))?;
            }
            RegistryType::Model => {
                self.registries.model.register_card(
                    card,
                    version_type,
                    pre_tag,
                    build_tag,
                    save_kwargs,
                )?;

                // update experimentcard_uids on experiment card
                let modelcard_uid = &card.getattr("uid")?.extract::<String>()?;
                self.experiment
                    .bind(py)
                    .call_method1("add_modelcard_uid", (modelcard_uid,))?;
            }

            RegistryType::Prompt => {
                self.registries.prompt.register_card(
                    card,
                    version_type,
                    pre_tag,
                    build_tag,
                    save_kwargs,
                )?;

                // update experimentcard_uids on experiment card
                let promptcard_uid = &card.getattr("uid")?.extract::<String>()?;
                self.experiment
                    .bind(py)
                    .call_method1("add_promptcard_uid", (promptcard_uid,))?;
            }

            _ => {
                warn!("Registry type not supported for {} when registering card from inside an experiment", registry_type);
            }
        }

        Ok(())
    }

    // work on logging artifacts
    // then registering other cards
}

/// Start an experiment
///
/// # Arguments
///
/// * `space` - The space URL
/// * `name` - The name of the experiment
/// * `code_dir` - The directory containing the code
/// * `log_hardware` - Whether to log hardware metrics. Will log hardware metrics every 30 seconds
/// * `experiment_uid` - The experiment UID
///
/// # Returns
///
/// * `Bound<Experiment>` - The experiment
///
/// # Errors
///
/// * `ExperimentError` - Error starting the experiment
#[pyfunction]
#[pyo3(signature = (space=None, name=None, code_dir=None, log_hardware=false, experiment_uid=None))]
#[instrument(skip_all)]
pub fn start_experiment<'py>(
    py: Python<'py>,
    space: Option<&str>,
    name: Option<&str>,
    code_dir: Option<PathBuf>,
    log_hardware: bool,
    experiment_uid: Option<&str>,
) -> PyResult<Bound<'py, Experiment>> {
    debug!("Initializing experiment");

    // runtime should be shared across all registries and all child experiments to prevent deadlocks

    let mut registries = CardRegistries::new()?;
    debug!("Experiment environment initialized");

    let active_experiment = match experiment_uid {
        Some(uid) => {
            let experiment = Experiment::load_experiment(py, uid, &mut registries)?;
            Experiment::new(
                py,
                experiment.unbind(),
                registries,
                false,
                None,
                uid.to_string(),
            )?
        }
        None => {
            let (experiment, uid) =
                Experiment::create_experiment(py, space, name, &mut registries, false)?;

            Experiment::new(
                py,
                experiment.unbind(),
                registries,
                log_hardware,
                code_dir,
                uid,
            )?
        }
    };

    Ok(Py::new(py, active_experiment)?.bind(py).clone())
}

#[pyfunction]
#[pyo3(signature = (experiment_uid, names = None))]
pub fn get_experiment_metrics(
    experiment_uid: &str,
    names: Option<Vec<String>>,
) -> PyResult<Metrics> {
    let metric_request = GetMetricRequest {
        experiment_uid: experiment_uid.to_string(),
        names: names.unwrap_or_default(),
    };

    let registry = OpsmlRegistry::new(RegistryType::Experiment)?;
    let metrics = registry.get_metrics(&metric_request)?;

    Ok(Metrics { metrics })
}

#[pyfunction]
#[pyo3(signature = (experiment_uid, names = None))]
pub fn get_experiment_parameters(
    experiment_uid: &str,
    names: Option<Vec<String>>,
) -> PyResult<Parameters> {
    let param_request = GetParameterRequest {
        experiment_uid: experiment_uid.to_string(),
        names: names.unwrap_or_default(),
    };

    let registry = OpsmlRegistry::new(RegistryType::Experiment)?;

    let parameters = registry.get_parameters(&param_request)?;

    Ok(Parameters { parameters })
}
