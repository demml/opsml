use opsml_app::{reloader::ReloadConfig, AppState};
use pyo3::prelude::*;

#[pymodule]
pub fn app(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<AppState>()?;
    m.add_class::<ReloadConfig>()?;
    Ok(())
}
