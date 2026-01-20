use crate::error::UtilError;
use pyo3::prelude::*;

pub fn extract_py_attr<'py, T>(
    interface: &Bound<'py, PyAny>,
    attr_name: &str,
) -> Result<T, UtilError>
where
    T: for<'a> FromPyObject<'a, 'py>,
{
    let attribute = interface.getattr(attr_name)?;
    attribute
        .extract::<T>()
        .map_err(|_| UtilError::PyError(format!("Failed to extract '{}", attr_name)))
}
