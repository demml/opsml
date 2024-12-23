use std::io;

use opsml_error::error::LoggingError;
use pyo3::prelude::*;
use tracing_subscriber;
use tracing_subscriber::fmt::time::UtcTime;

const DEFAULT_TIME_PATTERN: &str =
    "[year]-[month]-[day]T[hour repr:24]:[minute]:[second]::[subsecond digits:4]";

pub fn setup_logging(level: &str) -> Result<(), LoggingError> {
    let time_format = time::format_description::parse(DEFAULT_TIME_PATTERN).map_err(|e| {
        LoggingError::Error(format!(
            "Failed to parse time format: {} with error: {}",
            DEFAULT_TIME_PATTERN, e
        ))
    })?;

    let display_level = match level.to_lowercase().as_str() {
        "debug" => tracing::Level::DEBUG,
        "info" => tracing::Level::INFO,
        "warn" => tracing::Level::WARN,
        "error" => tracing::Level::ERROR,
        _ => tracing::Level::INFO,
    };

    tracing_subscriber::fmt()
        .with_max_level(display_level)
        .json()
        .with_target(false)
        .flatten_event(true)
        .with_thread_ids(true)
        .with_timer(UtcTime::new(time_format))
        .with_writer(io::stdout)
        .try_init()
        .map_err(|e| LoggingError::Error(format!("Failed to setup logging with error: {}", e)))?;

    Ok(())
}

#[pyclass]
pub struct OpsmlLogger {}

#[pymethods]
impl OpsmlLogger {
    #[staticmethod]
    #[pyo3(signature = (log_level=None))]
    pub fn setup_logging(log_level: Option<&str>) -> Result<(), LoggingError> {
        let log_level = log_level.unwrap_or("info");

        let _ = setup_logging(log_level).is_ok();

        Ok(())
    }
}
