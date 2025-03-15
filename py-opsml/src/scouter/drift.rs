use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn drift(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDrifter>()?;
    m.add_class::<DriftProfile>()?;
    m.add_class::<SpcDriftProfile>()?;
    m.add_class::<SpcFeatureDriftProfile>()?;
    m.add_class::<SpcDriftMap>()?;
    m.add_class::<SpcFeatureDrift>()?;
    m.add_class::<SpcDriftConfig>()?;
    m.add_class::<FeatureMap>()?;
    m.add_class::<PsiDriftConfig>()?;
    m.add_class::<PsiDriftProfile>()?;
    m.add_class::<Bin>()?;
    m.add_class::<PsiFeatureDriftProfile>()?;
    m.add_class::<PsiDriftMap>()?;
    m.add_class::<CustomMetric>()?;
    m.add_class::<CustomMetricDriftConfig>()?;
    m.add_class::<CustomDriftProfile>()?;
    Ok(())
}
