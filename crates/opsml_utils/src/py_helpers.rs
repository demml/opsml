use crate::error::UtilError;
use pyo3::prelude::*;

/// A helper function to extract a Python attribute and convert it to a specific type.
pub fn extract_py_attr<'py, T>(
    interface: &Bound<'py, PyAny>,
    attr_name: &str,
) -> Result<T, UtilError>
where
    T: FromPyObject<'py>,
{
    Ok(interface.getattr(attr_name)?.extract::<T>()?)
}
