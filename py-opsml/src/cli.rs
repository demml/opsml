use opsml_cli::{generate_key, install_app, lock_project, run_cli, run_demo};
use pyo3::prelude::*;
use std::env;

#[pyfunction]
pub fn run_opsml_cli() -> anyhow::Result<()> {
    let args: Vec<String> = env::args().collect();
    run_cli(args)
}

#[pymodule]
pub fn cli(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_opsml_cli, m)?)?;
    m.add_function(wrap_pyfunction!(lock_project, m)?)?;
    m.add_function(wrap_pyfunction!(install_app, m)?)?;
    m.add_function(wrap_pyfunction!(generate_key, m)?)?;
    m.add_function(wrap_pyfunction!(run_demo, m)?)?;
    Ok(())
}
