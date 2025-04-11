use opsml_error::OpsmlError;
use pyo3::prelude::*;

/// A helper function to extract a Python attribute and convert it to a specific type.
pub fn extract_py_attr<'py, T>(interface: &Bound<'py, PyAny>, attr_name: &str) -> PyResult<T>
where
    T: FromPyObject<'py>,
{
    interface
        .getattr(attr_name)
        .map_err(|e| OpsmlError::new_err(e.to_string()))?
        .extract::<T>()
        .map_err(|e| OpsmlError::new_err(e.to_string()))
}
