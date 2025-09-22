use opsml_cli::{
    download_card, generate_key, install_service, lock_service, run_cli,
    update_drift_profile_status, validate_project, DownloadCard, ScouterArgs,
};
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
    m.add_function(wrap_pyfunction!(lock_service, m)?)?;
    m.add_function(wrap_pyfunction!(install_service, m)?)?;
    m.add_function(wrap_pyfunction!(generate_key, m)?)?;
    m.add_function(wrap_pyfunction!(update_drift_profile_status, m)?)?;
    m.add_function(wrap_pyfunction!(validate_project, m)?)?;
    m.add_function(wrap_pyfunction!(download_card, m)?)?;

    m.add_class::<ScouterArgs>()?;
    m.add_class::<DownloadCard>()?;
    Ok(())
}
