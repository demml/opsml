use opsml_mocks::{OpenAITestServer, OpsmlServerContext, OpsmlTestServer};
use pyo3::prelude::*;
use scouter_client::MockConfig;

#[pymodule]
pub fn mock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    m.add_class::<OpsmlServerContext>()?;
    m.add_class::<OpenAITestServer>()?;
    m.add_class::<MockConfig>()?;
    Ok(())
}
