use opsml_cards::{CardInfo, DataCard, DataCardMetadata, Description};
use opsml_contracts::{Card, CardList};
use opsml_registry::PyCardRegistry;
#[cfg(feature = "server")]
use opsml_registry::RegistryTestHelper;

use pyo3::prelude::*;

#[pymodule]
pub fn card(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Description>()?;
    m.add_class::<CardInfo>()?;
    m.add_class::<Card>()?;
    m.add_class::<CardList>()?;
    m.add_class::<DataCard>()?;
    m.add_class::<DataCardMetadata>()?;

    // opsml_registry
    m.add_class::<PyCardRegistry>()?;

    #[cfg(feature = "server")]
    m.add_class::<RegistryTestHelper>()?;

    Ok(())
}
