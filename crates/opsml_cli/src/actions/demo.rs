use opsml_error::CliError;
use pyo3::prelude::*;

/// Runs opsml demo script
#[pyfunction]
pub fn run_demo() -> Result<(), CliError> {
    Python::with_gil(|py| {
        let demo = py.import("opsml.helpers.demo")?;
        let demo_func = demo.getattr("demo")?;
        demo_func.call1(())?;
        Ok(())
    })
    .map_err(|_: PyErr| CliError::PythonError)
}
