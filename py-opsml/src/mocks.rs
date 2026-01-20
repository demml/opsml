use opsml_mocks::{LLMTestServer, OpsmlServerContext, OpsmlTestServer};
use opsml_registry::RegistryTestHelper;
use pyo3::prelude::*;
use scouter_client::MockConfig;

pub fn add_mocks_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    m.add_class::<OpsmlServerContext>()?;
    m.add_class::<LLMTestServer>()?;
    m.add_class::<MockConfig>()?;
    m.add_class::<RegistryTestHelper>()?;

    Ok(())
}
