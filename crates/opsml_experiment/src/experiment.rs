use crate::error::ExperimentError;
use crate::HardwareQueue;
use chrono::{DateTime, Utc};

use opsml_cards::ExperimentCard;
use opsml_crypt::{decrypt_directory, encrypt_directory};
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
use tempfile::TempDir;
use tracing::{debug, error, instrument, warn};
use walkdir::WalkDir;
/// Get the filename of the python file
///
/// # Arguments
/// * `py` - The python interpreter
///
/// # Returns
/// * `PathBuf` - The path to the python file
///
/// # Errors
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
/// * `py` - The python interpreter
/// * `code_dir` - The directory containing the code
/// * `uid` - The experiment UID
/// * `fs` - The file system storage
/// * `registries` - The registries
/// * `rt` - The tokio runtime
///
/// # Returns
/// * `None`
///
/// # Errors
/// * `ExperimentError` - Error extracting the code
#[instrument(skip_all)]
fn extract_code(
    py: Python<'_>,
    code_dir: Option<PathBuf>,
    artifact_key: &ArtifactKey,
) -> Result<(), ExperimentError> {
    // Attempt to get file
    let (lpath, is_directory) = match code_dir {
        Some(path) => (path.to_path_buf(), path.is_dir()),
        None => {
            let py_file = get_py_filename(py)?;
            (py_file, false)
        }
    };

    let encryption_key = artifact_key.get_decrypt_key()?;

    // Create a temporary directory to copy the code to
    let temp_dir = TempDir::new()?;
    let temp_dir_path = temp_dir.path();

    // Set rpath and copy logic based on file or directory
    if is_directory {
        debug!(dir = ?lpath, "Copying directory");

        // For directories, create the directory structure in temp and set rpath to code directory
        let dest_dir = temp_dir_path.join(lpath.file_name().unwrap());

        for entry in WalkDir::new(&lpath) {
            let entry = entry?;
            let relative_path = entry.path().strip_prefix(&lpath)?;
            let dest_file_path = dest_dir.join(relative_path);

            if entry.file_type().is_file() {
                if let Some(parent) = dest_file_path.parent() {
                    std::fs::create_dir_all(parent)?;
                }
                std::fs::copy(entry.path(), &dest_file_path)?;
            }
        }
    } else {
        debug!(file = ?lpath, "Copying file");

        // For files, copy directly to temp directory and set rpath to code directory
        std::fs::copy(&lpath, temp_dir_path.join(lpath.file_name().unwrap()))?;
    };

    let rpath = artifact_key
        .storage_path()
        .join(SaveName::Artifacts)
        .join(SaveName::Code);

    // Encrypt the file or directory
    encrypt_directory(temp_dir_path, &encryption_key)?;

    // Upload the file or directory to the storage
    storage_client()?.put(temp_dir_path, &rpath, true)?;

    // Decrypt the file or directory (this is done to ensure the file is not encrypted in the code directory)
    decrypt_directory(temp_dir_path, &encryption_key)?;

    // Clean up the temporary directory
    temp_dir.close()?;

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
    ) -> Result<Self, ExperimentError> {
        // need artifact key for encryption/decryption

        let experiment_registry = &registries.experiment.registry;

        let artifact_key =
            experiment_registry.get_artifact_key(&experiment_uid, &RegistryType::Experiment)?;

        // extract card into ExperimentCard for adding needed fields for use outside of experiment
        // a little but of overhead here, but it's necessary
        // the card must be usable after the experiment is finished (downloading artifacts, etc.)
        let mut experiment: ExperimentCard = experiment.extract(py)?;
        experiment.set_artifact_key(artifact_key.clone());

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
            experiment: experiment.into_py_any(py)?,
            registries,
            hardware_queue,
            uid: experiment_uid,
            artifact_key,
        })
    }

    /// Create an experiment
    ///
    /// # Arguments
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
    /// * `Bound<PyAny>` - The experiment card
    /// * `String` - The experiment UID
    ///
    /// # Errors
    /// * `ExperimentError` - Error creating the experiment
    #[instrument(skip_all)]
    fn create_experiment<'py>(
        py: Python<'py>,
        space: Option<&str>,
        name: Option<&str>,
        registries: &mut CardRegistries,
        subexperiment: bool,
    ) -> Result<(Bound<'py, PyAny>, String), ExperimentError> {
        debug!("Initializing experiment");
        let experiment = Self::initialize_experiment(py, space, name, subexperiment)?;

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
    ) -> Result<Bound<'py, PyAny>, ExperimentError> {
        let mut card = ExperimentCard::new(py, space, name, None, None, None)?;
        card.subexperiment = subexperiment;

        let experiment = Py::new(py, card)?.into_bound_py_any(py)?;

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
    ) -> Result<String, ExperimentError> {
        registries
            .experiment
            .register_card(experiment, VersionType::Minor, None, None, None)?;

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
    ) -> Result<(), ExperimentError> {
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
    ) -> Result<Bound<'py, PyAny>, ExperimentError> {
        // Logic to load the existing experiment using the experiment_id
        let experiment = registries
            .experiment
            .load_card(py, Some(experiment_uid.to_string()), None, None, None, None)
            .map_err(ExperimentError::LoadCardError)?
            .into_bound_py_any(py)?;

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
    ) -> Result<Bound<'py, Experiment>, ExperimentError> {
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

    fn __enter__(slf: PyRef<'_, Self>) -> Result<PyRef<'_, Self>, ExperimentError> {
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
    ) -> Result<bool, ExperimentError> {
        if let (Some(exc_type), Some(exc_value), Some(traceback)) = (exc_type, exc_value, traceback)
        {
            error!(
                "An error occurred: {:?}, {:?}, {:?}",
                exc_type.to_string(),
                exc_value.to_string(),
                traceback.to_string()
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
    ) -> Result<(), ExperimentError> {
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

        registry
            .insert_metrics(&metric_request)
            .map_err(ExperimentError::InsertMetricError)?;

        Ok(())
    }

    pub fn log_metrics(&self, metrics: Vec<Metric>) -> Result<(), ExperimentError> {
        let registry = &self.registries.experiment.registry;

        let metric_request = MetricRequest {
            experiment_uid: self.uid.clone(),
            metrics,
        };

        registry
            .insert_metrics(&metric_request)
            .map_err(ExperimentError::InsertMetricError)?;

        Ok(())
    }

    #[pyo3(signature = (name, value))]
    pub fn log_parameter(
        &self,
        name: String,
        value: Bound<'_, PyAny>,
    ) -> Result<(), ExperimentError> {
        let registry = &self.registries.experiment.registry;

        let param_request = ParameterRequest {
            experiment_uid: self.uid.clone(),
            parameters: vec![Parameter::new(name, value)?],
        };

        registry
            .insert_parameters(&param_request)
            .map_err(ExperimentError::InsertParameterError)?;

        Ok(())
    }

    pub fn log_parameters(&self, parameters: Vec<Parameter>) -> Result<(), ExperimentError> {
        let registry = &self.registries.experiment.registry;

        let param_request = ParameterRequest {
            experiment_uid: self.uid.clone(),
            parameters,
        };

        registry
            .insert_parameters(&param_request)
            .map_err(ExperimentError::InsertParameterError)?;

        Ok(())
    }

    pub fn log_artifact(&self, path: PathBuf) -> Result<(), ExperimentError> {
        // get current working directory
        let cwd = std::env::current_dir()?;

        // check that path exists
        if !path.exists() {
            return Err(ExperimentError::PathNotExistError);
        }

        // check that path is a file
        if !path.is_file() {
            return Err(ExperimentError::PathNotFileError);
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

    fn log_artifacts(&self, path: PathBuf) -> Result<(), ExperimentError> {
        let encryption_key = self.artifact_key.get_decrypt_key()?;
        encrypt_directory(&path, &encryption_key)?;

        let rpath = self.artifact_key.storage_path().join(SaveName::Artifacts);

        storage_client()?.put(&path, &rpath, true)?;

        decrypt_directory(&path, &encryption_key)?;

        Ok(())
    }

    #[getter]
    pub fn card<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, ExperimentError> {
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
    ) -> Result<(), ExperimentError> {
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

            RegistryType::Deck => {
                self.registries.deck.register_card(
                    card,
                    version_type,
                    pre_tag,
                    build_tag,
                    save_kwargs,
                )?;

                // update experimentcard_uids on experiment card
                let deckcard_uid = &card.getattr("uid")?.extract::<String>()?;
                self.experiment
                    .bind(py)
                    .call_method1("add_card_deck_uid", (deckcard_uid,))?;
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
/// * `space` - The space URL
/// * `name` - The name of the experiment
/// * `code_dir` - The directory containing the code
/// * `log_hardware` - Whether to log hardware metrics. Will log hardware metrics every 30 seconds
/// * `experiment_uid` - The experiment UID
///
/// # Returns
/// * `Bound<Experiment>` - The experiment
///
/// # Errors
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
) -> Result<Bound<'py, Experiment>, ExperimentError> {
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
) -> Result<Metrics, ExperimentError> {
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
) -> Result<Parameters, ExperimentError> {
    let param_request = GetParameterRequest {
        experiment_uid: experiment_uid.to_string(),
        names: names.unwrap_or_default(),
    };

    let registry = OpsmlRegistry::new(RegistryType::Experiment)?;

    let parameters = registry.get_parameters(&param_request)?;

    Ok(Parameters { parameters })
}
