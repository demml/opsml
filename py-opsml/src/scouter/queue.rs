use pyo3::prelude::*;
use scouter_client::*;

pub fn add_queue_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SpcRecord>()?;
    m.add_class::<PsiRecord>()?;
    m.add_class::<CustomMetricRecord>()?;
    m.add_class::<LLMRecord>()?;
    m.add_class::<ServerRecord>()?;
    m.add_class::<ServerRecords>()?;
    m.add_class::<RecordType>()?;

    m.add_class::<Feature>()?;
    m.add_class::<Features>()?;
    m.add_class::<Metric>()?;
    m.add_class::<Metrics>()?;
    m.add_class::<EntityType>()?;

    // queue
    m.add_class::<QueueBus>()?;
    m.add_class::<ScouterQueue>()?;

    Ok(())
}
