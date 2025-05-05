use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn alert(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SpcAlertType>()?;
    m.add_class::<AlertZone>()?;
    m.add_class::<SpcAlert>()?;
    m.add_class::<SpcAlertRule>()?;
    m.add_class::<SpcAlertConfig>()?;
    m.add_class::<PsiAlertConfig>()?;
    m.add_class::<AlertThreshold>()?;
    m.add_class::<CustomMetricAlertCondition>()?;
    m.add_class::<CustomMetricAlertConfig>()?;
    m.add_class::<SlackDispatchConfig>()?;
    m.add_class::<OpsGenieDispatchConfig>()?;
    m.add_class::<ConsoleDispatchConfig>()?;
    m.add_class::<AlertDispatchType>()?;
    Ok(())
}
