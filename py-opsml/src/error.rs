use opsml_error::error::OpsmlError;
use pyo3::prelude::*;

#[pymodule]
pub fn error(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_errors
    m.add("OpsmlError", m.py().get_type::<OpsmlError>())?;

    Ok(())
}
