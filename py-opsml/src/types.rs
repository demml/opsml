use opsml_semver::VersionType;
use opsml_types::{CommonKwargs, DriftProfileUri, SaveName, SaverPath, Suffix};
use pyo3::prelude::*;

#[pymodule]
pub fn types(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CommonKwargs>()?;
    m.add_class::<SaveName>()?;
    m.add_class::<Suffix>()?;
    m.add_class::<VersionType>()?;
    m.add_class::<SaverPath>()?;
    m.add_class::<DriftProfileUri>()?;

    Ok(())
}
