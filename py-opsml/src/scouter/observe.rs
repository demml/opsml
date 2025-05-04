use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn observe(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LatencyMetrics>()?;
    m.add_class::<RouteMetrics>()?;
    m.add_class::<ObservabilityMetrics>()?;
    m.add_class::<Observer>()?;

    Ok(())
}
