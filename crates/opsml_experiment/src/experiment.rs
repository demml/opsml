use crate::HardwareQueue;
use names::Generator;
use opsml_cards::ExperimentCard;
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::{ExperimentError, OpsmlError};
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::contracts::MetricRequest;
use opsml_types::RegistryType;
use opsml_types::{
    cards::experiment::{Metric, Parameter},
    SaveName,
};
use pyo3::{prelude::*, IntoPyObjectExt};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tokio::sync::Mutex as TokioMutex;
use tracing::{debug, error, warn};

/// Initialize the experiment environment
///
///
/// # Returns
///
/// * `Arc<tokio::runtime::Runtime>` - The tokio runtime
/// * `Arc<Mutex<CardRegistries>` - The registries
/// * `Arc<TokioMutex<FileSystemStorage>>` - The file system storage
///
/// # Errors
///
/// * `ExperimentError` - Error initializing the experiment environment
fn initialize_experiment_environment() -> Result<
    (
        Arc<tokio::runtime::Runtime>,
        Arc<Mutex<CardRegistries>>,
        Arc<TokioMutex<FileSystemStorage>>,
    ),
    ExperimentError,
> {
    let rt = Arc::new(tokio::runtime::Runtime::new().unwrap());
    let registries = Arc::new(Mutex::new(CardRegistries::new_with_rt(rt.clone())?));
    let mut settings = OpsmlConfig::default().storage_settings()?;
    let fs = rt.block_on(async { FileSystemStorage::new(&mut settings).await })?;
    Ok((rt, registries, Arc::new(TokioMutex::new(fs))))
}

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
    uid: &str,
    fs: Arc<tokio::sync::Mutex<FileSystemStorage>>,
    registries: &mut std::sync::MutexGuard<'_, CardRegistries>,
    rt: Arc<tokio::runtime::Runtime>,
) -> Result<(), ExperimentError> {
    rt.block_on(async {
        // 1. Get artifact key
        let key = registries
            .experiment
            .registry
            .get_artifact_key(&uid, &RegistryType::Experiment)
            .await?;

        // Attempt to get file
        let (lpath, recursive) = match code_dir {
            Some(path) => (path.to_path_buf(), true),
            None => (get_py_filename(py)?, false),
        };

        // 2. Set rpath based on file or directory
        let rpath = if lpath.is_file() {
            &key.storage_path()
                .join(SaveName::Artifacts)
                .join(SaveName::Code)
                .join(lpath.file_name().unwrap())
        } else {
            &key.storage_path()
                .join(SaveName::Artifacts)
                .join(SaveName::Code)
        };

        let encryption_key = key.get_decrypt_key()?;

        // 3. Encrypt the file or directory
        encrypt_directory(&lpath, &encryption_key)?;

        // 4. Save the code to the storage
        fs.lock().await.put(&lpath, &rpath, recursive).await?;

        // 5. Decrypt the file or directory (this is done to ensure the file is not encrypted in the code directory)
        decrypt_directory(&lpath, &encryption_key)?;

        Ok::<(), ExperimentError>(())
    })
}

#[pyclass]
pub struct Experiment {
    pub experiment: PyObject,
    pub registries: Arc<Mutex<CardRegistries>>,
    pub fs: Arc<TokioMutex<FileSystemStorage>>,
    pub rt: Arc<tokio::runtime::Runtime>,
    pub hardware_queue: Option<HardwareQueue>,
    uid: String,
}

impl Experiment {
    pub fn new(
        experiment: PyObject,
        registries: Arc<Mutex<CardRegistries>>,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
        log_hardware: bool,
        experiment_uid: String,
    ) -> PyResult<Self> {
        let hardware_queue = match log_hardware {
            true => {
                // clone the experiment registry
                let registry = registries.lock().unwrap().experiment.registry.clone();
                let arc_reg = Arc::new(TokioMutex::new(registry));
                let hardware_queue =
                    HardwareQueue::start(rt.clone(), arc_reg, experiment_uid.clone())?;
                Some(hardware_queue)
            }

            false => None,
        };

        Ok(Self {
            experiment,
            registries,
            fs,
            rt,
            hardware_queue,
            uid: experiment_uid,
        })
    }

    fn unlock_registries(&self) -> PyResult<std::sync::MutexGuard<'_, CardRegistries>> {
        let registries = self.registries.lock().map_err(|e| {
            error!("Failed to lock registries: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(registries)
    }

    /// Create an experiment
    ///
    /// # Arguments
    ///
    /// * `py` - The python interpreter
    /// * `repository` - The repository URL
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
    fn create_experiment<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        code_dir: Option<PathBuf>,
        mut registries: std::sync::MutexGuard<'_, CardRegistries>,
        subexperiment: bool,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> PyResult<(Bound<'py, PyAny>, String)> {
        let name = name.map(String::from).unwrap_or_else(|| {
            let mut generator = Generator::default();
            generator.next().unwrap_or_else(|| "experiment".to_string())
        });

        let experiment = Self::initialize_experiment(py, repository, Some(&name), subexperiment)?;

        let uid = Self::register_experiment(&experiment, &mut registries, code_dir, fs, rt)?;
        Ok((experiment, uid))
    }

    /// Initialize the experiment
    ///
    /// # Arguments
    ///
    /// * `py` - The python interpreter
    /// * `repository` - The repository URL
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
        repository: Option<&str>,
        name: Option<&str>,
        subexperiment: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let mut card = ExperimentCard::new(py, repository, name, None, None, None)?;
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
    fn register_experiment<'py>(
        experiment: &Bound<'py, PyAny>,
        registries: &mut std::sync::MutexGuard<'_, CardRegistries>,
        code_dir: Option<PathBuf>,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> PyResult<String> {
        registries
            .experiment
            .register_card(experiment, VersionType::Minor, None, None, None)
            .map_err(|e| {
                error!("Failed to register experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let uid = experiment.getattr("uid")?.extract::<String>()?;
        let py = experiment.py();

        match extract_code(py, code_dir, &uid, fs, registries, rt) {
            Ok(_) => debug!("Code extracted successfully"),
            Err(e) => warn!("Failed to extract code: {}", e),
        }

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
    fn load_experiment<'py>(
        py: Python<'py>,
        experiment_uid: &str,
        mut registries: std::sync::MutexGuard<'_, CardRegistries>,
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
    /// * `repository` - The repository URL
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
    #[pyo3(signature = (repository=None, name=None, code_dir=None, log_hardware=false, experiment_uid=None))]
    pub fn start_experiment<'py>(
        slf: PyRefMut<'py, Self>,
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        code_dir: Option<PathBuf>,
        log_hardware: bool,
        experiment_uid: Option<&str>,
    ) -> PyResult<Bound<'py, Experiment>> {
        let experiment = match experiment_uid {
            Some(uid) => {
                let card = Experiment::load_experiment(py, uid, slf.unlock_registries()?)?;
                Experiment::new(
                    card.unbind(),
                    slf.registries.clone(),
                    slf.fs.clone(),
                    slf.rt.clone(),
                    false, // we can always revisit, but it doesn't make sense to log hardware for a completed experiment
                    uid.to_string(),
                )?
            }
            None => {
                let (card, uid) = Experiment::create_experiment(
                    py,
                    repository,
                    name,
                    code_dir,
                    slf.unlock_registries()?,
                    true,
                    slf.fs.clone(),
                    slf.rt.clone(),
                )?;

                Experiment::new(
                    card.unbind(),
                    slf.registries.clone(),
                    slf.fs.clone(),
                    slf.rt.clone(),
                    log_hardware,
                    uid,
                )?
            }
        };

        // Add the new experiment's UID to the parent experiment's experimentcard_uids
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
        &mut self,
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
            // update card
            self.unlock_registries()?
                .experiment
                .update_card(self.experiment.bind(py))?;

            debug!("Stopping hardware queue");
            self.stop_queue()?;

            debug!("Experiment updated");
        }

        Ok(false) // Return false to propagate exceptions
    }

    pub fn insert_metric(&self, metric: Metric) -> PyResult<()> {
        let mut registry = self.registries.lock().unwrap().experiment.registry.clone();

        let metric_request = MetricRequest {
            experiment_uid: self.uid.clone(),
            metrics: vec![metric],
        };

        let response = self
            .rt
            .block_on(async { registry.insert_metrics(&metric_request).await })?;

        Ok(())
    }
}

/// Start an experiment
///
/// # Arguments
///
/// * `repository` - The repository URL
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
#[pyo3(signature = (repository=None, name=None, code_dir=None, log_hardware=false, experiment_uid=None))]
pub fn start_experiment<'py>(
    py: Python<'py>,
    repository: Option<&str>,
    name: Option<&str>,
    code_dir: Option<PathBuf>,
    log_hardware: bool,
    experiment_uid: Option<&str>,
) -> PyResult<Bound<'py, Experiment>> {
    debug!("Initializing experiment");

    // runtime should be shared across all registries and all child experiments to prevent deadlocks
    let (rt, registries, fs) = initialize_experiment_environment()?;

    let active_experiment = match experiment_uid {
        Some(uid) => {
            let card = Experiment::load_experiment(py, uid, registries.lock().unwrap())?;
            Experiment::new(card.unbind(), registries, fs, rt, false, uid.to_string())?
        }
        None => {
            let (card, uid) = Experiment::create_experiment(
                py,
                repository,
                name,
                code_dir,
                registries.lock().unwrap(),
                false,
                fs.clone(),
                rt.clone(),
            )?;

            Experiment::new(card.unbind(), registries, fs, rt, log_hardware, uid)?
        }
    };

    Ok(Py::new(py, active_experiment)?.bind(py).clone())
}
