pub mod error;
pub use error::*;
use pyo3::PyResult;
use tracing::error;

/// Helper function to wrap Results that should return a PyResult
pub fn map_err_with_logging<T, E>(result: Result<T, E>, context: &str) -> PyResult<T>
where
    E: std::fmt::Display,
{
    result.map_err(|e| {
        let msg = format!("{}: {}", context, e);
        error!(msg);
        crate::OpsmlError::new_err(msg)
    })
}
