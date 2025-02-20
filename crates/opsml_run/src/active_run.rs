use crate::RunCard;
use opsml_error::{CardError, OpsmlError};
use opsml_registry::CardRegistries;
use opsml_semver::VersionType;
use pyo3::{prelude::*, IntoPyObjectExt};
use std::sync::{Arc, Mutex};
use tracing::{debug, error};

#[pyclass]
pub struct ActiveRun {
    pub run: PyObject,
    pub registries: Arc<Mutex<CardRegistries>>,
}

impl ActiveRun {
    pub fn new(run: PyObject, registries: Arc<Mutex<CardRegistries>>) -> PyResult<Self> {
        Ok(Self { run, registries })
    }

    fn unlock_registries(&self) -> PyResult<std::sync::MutexGuard<'_, CardRegistries>> {
        let registries = self.registries.lock().map_err(|e| {
            error!("Failed to lock registries: {}", e);
            CardError::Error(e.to_string())
        })?;

        Ok(registries)
    }

    fn create_run_card<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        log_hardware: Option<bool>,
        code_dir: Option<&str>,
        mut registries: std::sync::MutexGuard<'_, CardRegistries>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let run = Self::initialize_run_card(py, repository, name, log_hardware, code_dir)?;
        Self::register_run_card(&run, &mut registries)?;
        Ok(run)
    }

    fn initialize_run_card<'py>(
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        log_hardware: Option<bool>,
        code_dir: Option<&str>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let _hardware = log_hardware.unwrap_or(false);
        let _code_dir = code_dir.unwrap_or("");

        let run = Py::new(py, RunCard::new(py, repository, name, None, None, None)?)?
            .into_bound_py_any(py)
            .map_err(|e| {
                error!("Failed to register run card: {}", e);
                CardError::Error(e.to_string())
            })?;

        Ok(run)
    }

    fn register_run_card<'py>(
        run: &Bound<'py, PyAny>,
        registries: &mut std::sync::MutexGuard<'_, CardRegistries>,
    ) -> PyResult<()> {
        registries
            .run
            .register_card(run, VersionType::Minor, None, None, None)
            .map_err(|e| {
                error!("Failed to register run card: {}", e);
                OpsmlError::new_err(e.to_string())
            })
    }

    fn add_child_run<'py>(
        slf: &PyRefMut<'py, Self>,
        py: Python<'py>,
        run: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let child_uid = run.getattr("uid")?.extract::<String>()?;
        slf.run.call_method1(py, "add_child_run", (&child_uid,))?;
        Ok(())
    }
}

#[pymethods]
impl ActiveRun {
    #[pyo3(signature = (repository=None, name=None, log_hardware=None, code_dir=None))]
    pub fn start_run<'py>(
        slf: PyRefMut<'py, Self>,
        py: Python<'py>,
        repository: Option<&str>,
        name: Option<&str>,
        log_hardware: Option<bool>,
        code_dir: Option<&str>,
    ) -> PyResult<Bound<'py, ActiveRun>> {
        let run = Self::create_run_card(
            py,
            repository,
            name,
            log_hardware,
            code_dir,
            slf.unlock_registries()?,
        )?;

        // Add the new run's UID to the parent run's runcard_uids
        Self::add_child_run(&slf, py, &run)?;

        debug!("Starting run: {}", run.getattr("uid")?.extract::<String>()?);

        // Return the new ActiveRun wrapped in a PyRef which implements context manager protocol
        let active = ActiveRun::new(run.unbind(), slf.registries.clone())?;

        Ok(Py::new(py, active)?.bind(py).clone())
    }

    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        debug!("Starting run");
        Ok(slf)
    }

    #[pyo3(signature = (exc_type=None, exc_value=None, traceback=None))]
    fn __exit__(
        &self,
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
            println!("Exiting the context without error");
        }

        Ok(false) // Return false to propagate exceptions
    }
}

//run_name: str | None = None,
//log_hardware: bool = False,
//hardware_interval: int = _DEFAULT_INTERVAL,
//code_dir: str | Path | None = None
