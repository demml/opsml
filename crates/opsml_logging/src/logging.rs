use std::io;

use dynfmt::{Format, SimpleCurlyFormat};
use opsml_error::error::LoggingError;
use opsml_types::LogLevel;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use pyo3::types::PyTupleMethods;
use tracing_subscriber;
use tracing_subscriber::fmt::time::UtcTime;

#[allow(clippy::len_zero)] // len tends to be faster than is_empty in tests
fn format_string(message: &str, args: &Vec<String>) -> String {
    if args.len() > 0 {
        SimpleCurlyFormat
            .format(message, args)
            .unwrap_or_else(|_| message.into())
            .to_string()
    } else {
        message.to_string()
    }
}

pub fn parse_args(args: Bound<'_, PyTuple>) -> Option<Vec<String>> {
    if args.is_empty() {
        None
    } else {
        Some(args.iter().map(|x| x.to_string()).collect())
    }
}

const DEFAULT_TIME_PATTERN: &str =
    "[year]-[month]-[day]T[hour repr:24]:[minute]:[second]::[subsecond digits:4]";

pub fn setup_logging(level: &LogLevel) -> Result<(), LoggingError> {
    let time_format = time::format_description::parse(DEFAULT_TIME_PATTERN).map_err(|e| {
        LoggingError::Error(format!(
            "Failed to parse time format: {} with error: {}",
            DEFAULT_TIME_PATTERN, e
        ))
    })?;

    let display_level = match level {
        LogLevel::Debug => tracing::Level::DEBUG,
        LogLevel::Info => tracing::Level::INFO,
        LogLevel::Warn => tracing::Level::WARN,
        LogLevel::Error => tracing::Level::ERROR,
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
    pub fn setup_logging(log_level: Option<LogLevel>) -> Result<(), LoggingError> {
        let log_level = log_level.unwrap_or(LogLevel::Info);

        let _ = setup_logging(&log_level).is_ok();

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (log_level=None))]
    pub fn get_logger(log_level: Option<LogLevel>) -> PyResult<OpsmlLogger> {
        let log_level = log_level.unwrap_or(LogLevel::Info);

        let _ = setup_logging(&log_level).is_ok();

        Ok(OpsmlLogger {})
    }

    #[pyo3(signature = (message, *args))]
    pub fn info(&self, message: &str, args: Bound<'_, PyTuple>) {
        let args = parse_args(args);
        let msg = match args {
            Some(val) => format_string(message, &val),
            None => message.to_string(),
        };
        tracing::info!(msg);
    }

    #[pyo3(signature = (message, *args))]
    pub fn debug(&self, message: &str, args: Bound<'_, PyTuple>) {
        let args = parse_args(args);
        let msg = match args {
            Some(val) => format_string(message, &val),
            None => message.to_string(),
        };
        tracing::debug!(msg);
    }

    #[pyo3(signature = (message, *args))]
    pub fn warn(&self, message: &str, args: Bound<'_, PyTuple>) {
        let args = parse_args(args);
        let msg = match args {
            Some(val) => format_string(message, &val),
            None => message.to_string(),
        };
        tracing::warn!(msg);
    }

    #[pyo3(signature = (message, *args))]
    pub fn error(&self, message: &str, args: Bound<'_, PyTuple>) {
        let args = parse_args(args);
        let msg = match args {
            Some(val) => format_string(message, &val),
            None => message.to_string(),
        };
        tracing::error!(msg);
    }
}
