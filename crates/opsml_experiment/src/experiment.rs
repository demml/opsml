use names::Generator;
use opsml_cards::ExperimentCard;
use opsml_crypt::{decrypt_directory, encrypt_directory};
use opsml_error::{ExperimentError, OpsmlError};
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use opsml_types::RegistryType;
use opsml_types::SaveName;
use pyo3::{prelude::*, IntoPyObjectExt};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tokio::sync::Mutex as TokioMutex;
use tracing::{debug, error};

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

fn get_py_filename(py: Python) -> Result<PathBuf, ExperimentError> {
    let inspect = py.import("inspect")?;
    let current_frame = inspect.call_method0("currentframe")?;
    let f_code = current_frame.getattr("f_code")?;
    let filename = f_code.getattr("co_filename")?;

    Ok(PathBuf::from(filename.to_string()))
}

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
}

impl Experiment {
    pub fn new(
        experiment: PyObject,
        registries: Arc<Mutex<CardRegistries>>,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> PyResult<Self> {
        Ok(Self {
            experiment,
            registries,
            fs,
            rt,
        })
    }

    fn unlock_registries(&self) -> PyResult<std::sync::MutexGuard<'_, CardRegistries>> {
        let registries = self.registries.lock().map_err(|e| {
            error!("Failed to lock registries: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(registries)
    }

    fn create_experiment<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        code_dir: Option<PathBuf>,
        log_hardware: bool,
        mut registries: std::sync::MutexGuard<'_, CardRegistries>,
        subexperiment: bool,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let name = name.map(String::from).unwrap_or_else(|| {
            let mut generator = Generator::default();
            generator.next().unwrap_or_else(|| "experiment".to_string())
        });

        let experiment = Self::initialize_experiment(py, repository, Some(&name), subexperiment)?;

        Self::register_experiment(&experiment, &mut registries, code_dir, log_hardware, fs, rt)?;
        Ok(experiment)
    }

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

    fn register_experiment<'py>(
        experiment: &Bound<'py, PyAny>,
        registries: &mut std::sync::MutexGuard<'_, CardRegistries>,
        code_dir: Option<PathBuf>,
        _log_hardware: bool,
        fs: Arc<TokioMutex<FileSystemStorage>>,
        rt: Arc<tokio::runtime::Runtime>,
    ) -> PyResult<()> {
        registries
            .experiment
            .register_card(experiment, VersionType::Minor, None, None, None)
            .map_err(|e| {
                error!("Failed to register experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let uid = experiment.getattr("uid")?.extract::<String>()?;
        let py = experiment.py();

        extract_code(py, code_dir, &uid, fs, registries, rt)?;

        Ok(())
    }

    fn add_subexperiment_experiment<'py>(
        slf: &PyRefMut<'py, Self>,
        py: Python<'py>,
        experiment: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let subexperiment_uid = experiment.getattr("uid")?.extract::<String>()?;
        slf.experiment
            .call_method1(py, "add_subexperiment_experiment", (&subexperiment_uid,))?;
        Ok(())
    }

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
}

#[pymethods]
impl Experiment {
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
        let experiment = if let Some(experiment_uid) = experiment_uid {
            // Load the existing experiment
            Self::load_experiment(py, experiment_uid, slf.unlock_registries()?)?
        } else {
            // Create a new experiment
            Self::create_experiment(
                py,
                repository,
                name,
                code_dir,
                log_hardware,
                slf.unlock_registries()?,
                true,
                slf.fs.clone(),
                slf.rt.clone(),
            )?
        };

        // Add the new experiment's UID to the parent experiment's experimentcard_uids
        Self::add_subexperiment_experiment(&slf, py, &experiment)?;

        debug!(
            "Starting experiment: {}",
            experiment.getattr("uid")?.extract::<String>()?
        );

        // Return the new Activeexperiment wrapped in a PyRef which implements context manager protocol
        let active = Experiment::new(
            experiment.unbind(),
            slf.registries.clone(),
            slf.fs.clone(),
            slf.rt.clone(),
        )?;

        Ok(Py::new(py, active)?.bind(py).clone())
    }

    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        debug!("Starting experiment");
        Ok(slf)
    }

    #[pyo3(signature = (exc_type=None, exc_value=None, traceback=None))]
    fn __exit__(
        &self,
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

            debug!("Experiment updated");
        }

        Ok(false) // Return false to propagate exceptions
    }
}

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
    // runtime should be shared across all registries
    let (rt, registries, fs) = initialize_experiment_environment()?;

    let experiment = if let Some(experiment_uid) = experiment_uid {
        // Load the existing experiment
        Experiment::load_experiment(py, experiment_uid, registries.lock().unwrap())?
    } else {
        // Create a new experiment
        Experiment::create_experiment(
            py,
            repository,
            name,
            code_dir,
            log_hardware,
            registries.lock().unwrap(),
            false,
            fs.clone(),
            rt.clone(),
        )?
    };

    // Return the new Active experiment wrapped in a PyRef which implements context manager protocol
    let active = Experiment::new(experiment.unbind(), registries, fs, rt)?;

    Ok(Py::new(py, active)?.bind(py).clone())
}
