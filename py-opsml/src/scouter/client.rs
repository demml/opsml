use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn client(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ScouterClient>()?;
    m.add_class::<DriftRequest>()?;
    m.add_class::<ProfileStatusRequest>()?;
    m.add_class::<DriftAlertRequest>()?;
    m.add_class::<Alert>()?;

    m.add_class::<TimeInterval>()?;

    m.add_class::<BinnedCustomMetricStats>()?;
    m.add_class::<BinnedCustomMetric>()?;
    m.add_class::<BinnedCustomMetrics>()?;

    m.add_class::<BinnedPsiFeatureMetrics>()?;
    m.add_class::<BinnedPsiMetric>()?;

    m.add_class::<SpcDriftFeatures>()?;
    m.add_class::<SpcDriftFeature>()?;

    m.add_class::<HTTPConfig>()?;

    Ok(())
}
