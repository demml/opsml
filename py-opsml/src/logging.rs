use rusty_logging::{logger::WriteLevel, LogLevel, LoggingConfig, RustyLogger};

use pyo3::prelude::*;
use std::env;
use std::str::FromStr;

#[pyfunction]
fn _get_log_level() -> Option<LogLevel> {
    // check if LOG_LEVEL env var is set
    match env::var("LOG_LEVEL") {
        Ok(level_str) => LogLevel::from_str(&level_str).ok(),
        Err(_) => None,
    }
}

#[pyfunction]
fn _log_json() -> bool {
    // check if LOG_JSON is set to "1" or "true"
    match env::var("LOG_JSON") {
        Ok(val) => val == "1" || val.to_lowercase() == "true",
        Err(_) => false,
    }
}

pub fn add_logging_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<LogLevel>()?;
    m.add_class::<LoggingConfig>()?;
    m.add_class::<RustyLogger>()?;
    m.add_class::<WriteLevel>()?;
    m.add_function(wrap_pyfunction!(_get_log_level, m)?)?;
    m.add_function(wrap_pyfunction!(_log_json, m)?)?;
    Ok(())
}
