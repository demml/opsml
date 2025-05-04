use rusty_logging::{logger::WriteLevel, LogLevel, LoggingConfig, RustyLogger};

use pyo3::prelude::*;

#[pymodule]
pub fn logging(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<LogLevel>()?;
    m.add_class::<LoggingConfig>()?;
    m.add_class::<RustyLogger>()?;
    m.add_class::<WriteLevel>()?;
    Ok(())
}
