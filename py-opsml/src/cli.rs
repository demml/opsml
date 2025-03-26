use opsml_cli::run_cli;
use pyo3::prelude::*;
use std::env;

#[pyfunction]
pub fn run_opsml_cli() -> PyResult<()> {
    let args: Vec<String> = env::args().collect();

    // Skip the first argument (script name) and pass the rest to run_cli
    match run_cli(args) {
        Ok(_) => Ok(()),
        Err(e) => {
            // Convert anyhow::Error to PyErr
            Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
        }
    }
}
