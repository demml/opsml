use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn profile(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DataProfile>()?;
    m.add_class::<FeatureProfile>()?;
    m.add_class::<Distinct>()?;
    m.add_class::<Histogram>()?;
    m.add_class::<Quantiles>()?;
    m.add_class::<NumericStats>()?;
    m.add_class::<StringStats>()?;
    m.add_class::<CharStats>()?;
    m.add_class::<WordStats>()?;
    m.add_class::<DataProfiler>()?;

    Ok(())
}
