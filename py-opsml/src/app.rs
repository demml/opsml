use opsml_app::{reloader::ReloadConfig, AppState};
use pyo3::prelude::*;

pub fn add_app_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<AppState>()?;
    m.add_class::<ReloadConfig>()?;
    Ok(())
}
