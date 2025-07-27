use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn client(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyScouterClient>()?;
    m.add_class::<DriftRequest>()?;
    m.add_class::<ProfileStatusRequest>()?;
    m.add_class::<DriftAlertRequest>()?;
    m.add_class::<GetProfileRequest>()?;
    m.add_class::<Alert>()?;

    m.add_class::<TimeInterval>()?;

    m.add_class::<BinnedMetricStats>()?;
    m.add_class::<BinnedMetric>()?;
    m.add_class::<BinnedMetrics>()?;

    m.add_class::<BinnedPsiFeatureMetrics>()?;
    m.add_class::<BinnedPsiMetric>()?;

    m.add_class::<SpcDriftFeatures>()?;
    m.add_class::<SpcDriftFeature>()?;

    m.add_class::<HTTPConfig>()?;

    Ok(())
}
