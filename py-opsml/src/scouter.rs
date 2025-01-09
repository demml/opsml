use scouter_client::*;

use pyo3::prelude::*;

#[pymodule]
pub fn scouter(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // scouter_client (we need to re-export types, so that we don't need to install scouter on the python side)
    // opsml_errors
    m.add("ScouterError", m.py().get_type::<PyScouterError>())?;
    m.add_class::<SpcDrifter>()?;
    m.add_class::<SpcDriftProfile>()?;
    m.add_class::<SpcFeatureDriftProfile>()?;
    m.add_class::<DataProfile>()?;
    m.add_class::<FeatureProfile>()?;
    m.add_class::<Distinct>()?;
    m.add_class::<Histogram>()?;
    m.add_class::<SpcDriftMap>()?;
    m.add_class::<SpcFeatureDrift>()?;
    m.add_class::<SpcDriftConfig>()?;
    m.add_class::<SpcAlertType>()?;
    m.add_class::<AlertZone>()?;
    m.add_class::<SpcAlert>()?;
    m.add_class::<PsiDriftConfig>()?;
    m.add_class::<SpcFeatureAlerts>()?;
    m.add_class::<SpcFeatureAlert>()?;
    m.add_class::<SpcAlertRule>()?;
    m.add_class::<Every1Minute>()?;
    m.add_class::<Every5Minutes>()?;
    m.add_class::<Every15Minutes>()?;
    m.add_class::<Every30Minutes>()?;
    m.add_class::<EveryHour>()?;
    m.add_class::<Every6Hours>()?;
    m.add_class::<Every12Hours>()?;
    m.add_class::<EveryDay>()?;
    m.add_class::<EveryWeek>()?;
    m.add_class::<CommonCron>()?;
    m.add_class::<SpcAlertConfig>()?;
    m.add_class::<AlertDispatchType>()?;
    m.add_class::<FeatureMap>()?;
    m.add_class::<SpcFeatureQueue>()?;
    m.add_class::<PsiFeatureQueue>()?;
    m.add_class::<DriftType>()?;
    m.add_class::<RecordType>()?;
    m.add_class::<ServerRecords>()?;
    m.add_class::<SpcServerRecord>()?;
    m.add_class::<PsiServerRecord>()?;
    m.add_class::<ServerRecord>()?;
    m.add_class::<Observer>()?;
    m.add_class::<RouteMetrics>()?;
    m.add_class::<LatencyMetrics>()?;
    m.add_class::<ObservabilityMetrics>()?;
    m.add_class::<PsiAlertConfig>()?;
    m.add_class::<Bin>()?;
    m.add_class::<PsiFeatureDriftProfile>()?;
    m.add_class::<PsiDriftProfile>()?;
    m.add_class::<PsiDriftMap>()?;
    m.add_class::<PsiDrifter>()?;
    m.add_class::<CustomMetricAlertCondition>()?;
    m.add_class::<CustomMetricAlertConfig>()?;
    m.add_class::<CustomMetricDriftConfig>()?;
    m.add_class::<CustomMetric>()?;
    m.add_class::<AlertThreshold>()?;
    m.add_class::<CustomDriftProfile>()?;
    m.add_class::<CustomDrifter>()?;
    m.add_class::<CustomMetricServerRecord>()?;
    m.add_class::<Feature>()?;
    m.add_class::<Features>()?;
    m.add_class::<DataProfiler>()?;

    Ok(())
}
