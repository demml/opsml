use names::Generator;
use opsml_cards::ExperimentCard;
use opsml_error::{ExperimentError, OpsmlError};
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;
use opsml_storage::FileSystemStorage;
use pyo3::{prelude::*, IntoPyObjectExt};
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
        code_dir: Option<&str>,
        log_hardware: bool,
        mut registries: std::sync::MutexGuard<'_, CardRegistries>,
        child: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let name = name.map(String::from).unwrap_or_else(|| {
            let mut generator = Generator::default();
            generator.next().unwrap_or_else(|| "experiment".to_string())
        });

        let experiment = Self::initialize_experiment(
            py,
            repository,
            Some(&name),
            code_dir,
            log_hardware,
            child,
        )?;
        Self::register_experiment(&experiment, &mut registries)?;
        Ok(experiment)
    }

    fn initialize_experiment<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        code_dir: Option<&str>,
        log_hardware: bool,
        child: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let _hardware = log_hardware;
        let _code_dir = code_dir.unwrap_or("");

        let mut card = ExperimentCard::new(py, repository, name, None, None, None)?;
        card.child = child;

        let experiment = Py::new(py, card)?.into_bound_py_any(py).map_err(|e| {
            error!("Failed to register experiment card: {}", e);
            ExperimentError::Error(e.to_string())
        })?;

        Ok(experiment)
    }

    fn register_experiment<'py>(
        experiment: &Bound<'py, PyAny>,
        registries: &mut std::sync::MutexGuard<'_, CardRegistries>,
    ) -> PyResult<()> {
        registries
            .experiment
            .register_card(experiment, VersionType::Minor, None, None, None)
            .map_err(|e| {
                error!("Failed to register experiment card: {}", e);
                OpsmlError::new_err(e.to_string())
            })
    }

    fn add_child_experiment<'py>(
        slf: &PyRefMut<'py, Self>,
        py: Python<'py>,
        experiment: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let child_uid = experiment.getattr("uid")?.extract::<String>()?;
        slf.experiment
            .call_method1(py, "add_child_experiment", (&child_uid,))?;
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
        code_dir: Option<&str>,
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
            )?
        };

        // Add the new experiment's UID to the parent experiment's experimentcard_uids
        Self::add_child_experiment(&slf, py, &experiment)?;

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
    code_dir: Option<&str>,
    log_hardware: bool,
    experiment_uid: Option<&str>,
) -> PyResult<Bound<'py, Experiment>> {
    debug!("Initializing experiment");
    // runtime should be shared across all registries
    let (rt, registries, fs) = initialize_experiment_environment()?;

    debug!("Creating experiment");
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
        )?
    };

    // Return the new Active experiment wrapped in a PyRef which implements context manager protocol
    let active = Experiment::new(experiment.unbind(), registries, fs, rt)?;

    Ok(Py::new(py, active)?.bind(py).clone())
}
