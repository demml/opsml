use crate::RunCard;
use opsml_error::CardError;
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
        let run = Py::new(py, RunCard::new(py, repository, name, None, None, None)?)?
            .into_bound_py_any(py)
            .map_err(|e| {
                error!("Failed to register run card: {}", e);
                CardError::Error(e.to_string())
            })?;

        slf.registries.lock().unwrap().run.register_card(
            &run,
            VersionType::Minor,
            None,
            None,
            None,
        )?;

        let _hardware = log_hardware.unwrap_or(false);
        let _code_dir = code_dir.unwrap_or("");

        // Add the new run's UID to the parent run's runcard_uids
        slf.run
            .call_method1(py, "add_child_run", (&run.getattr("uid")?,))?;

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
