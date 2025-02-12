use opsml_registry::CardRegistry;
use opsml_types::contracts::{Card, CardList};
use opsml_types::{RegistryMode, RegistryType};
use pyo3::prelude::*;

#[pymodule]
pub fn registry(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CardRegistry>()?;
    m.add_class::<RegistryType>()?;
    m.add_class::<RegistryMode>()?;
    m.add_class::<Card>()?;
    m.add_class::<CardList>()?;
    Ok(())
}
