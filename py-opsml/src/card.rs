use opsml_cards::{DataCard, DataCardMetadata, ModelCard, ModelCardMetadata};
use opsml_registry::CardRegistry;
#[cfg(feature = "server")]
use opsml_registry::RegistryTestHelper;
use opsml_types::contracts::{Card, CardList};
use opsml_types::{RegistryMode, RegistryType};

use pyo3::prelude::*;

#[pymodule]
pub fn card(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Card>()?;
    m.add_class::<CardList>()?;
    m.add_class::<DataCard>()?;
    m.add_class::<DataCardMetadata>()?;

    // opsml_registry
    m.add_class::<CardRegistry>()?;
    m.add_class::<RegistryType>()?;
    m.add_class::<RegistryMode>()?;

    #[cfg(feature = "server")]
    m.add_class::<RegistryTestHelper>()?;

    // ModelCard
    m.add_class::<ModelCard>()?;
    m.add_class::<ModelCardMetadata>()?;

    Ok(())
}
