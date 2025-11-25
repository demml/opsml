use pyo3::prelude::*;
use scouter_client::*;

pub fn add_client_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
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

    m.add_class::<Attribute>()?;
    m.add_class::<SpanEvent>()?;
    m.add_class::<SpanLink>()?;
    m.add_class::<TraceBaggageRecord>()?;
    m.add_class::<TraceFilters>()?;
    m.add_class::<TraceMetricBucket>()?;
    m.add_class::<TraceListItem>()?;
    m.add_class::<TraceSpan>()?;
    m.add_class::<TracePaginationResponse>()?;
    m.add_class::<TraceBaggageResponse>()?;
    m.add_class::<TraceSpansResponse>()?;
    m.add_class::<TraceMetricsRequest>()?;
    m.add_class::<TraceMetricsResponse>()?;
    m.add_class::<TagRecord>()?;
    m.add_class::<TagsResponse>()?;

    Ok(())
}
