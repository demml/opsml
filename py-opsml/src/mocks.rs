use opsml_mocks::{OpsmlServerContext, OpsmlTestServer};
use opsml_registry::RegistryTestHelper;
use potato_head::LLMTestServer;
use pyo3::prelude::*;
use scouter_client::MockConfig;

#[pymodule]
pub fn mock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    m.add_class::<OpsmlServerContext>()?;
    m.add_class::<LLMTestServer>()?;
    m.add_class::<MockConfig>()?;
    m.add_class::<LLMTestServer>()?;
    m.add_class::<RegistryTestHelper>()?;

    Ok(())
}
