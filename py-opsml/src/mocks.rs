use opsml_mocks::{OpenAITestServer, OpsmlServerContext, OpsmlTestServer};
use pyo3::prelude::*;

#[pymodule]
pub fn mock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OpsmlTestServer>()?;
    m.add_class::<OpsmlServerContext>()?;
    m.add_class::<OpenAITestServer>()?;
    Ok(())
}
