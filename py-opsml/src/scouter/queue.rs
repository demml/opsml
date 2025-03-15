use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn queue(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ScouterQueue>()?;
    m.add_class::<ScouterProducer>()?;
    m.add_class::<KafkaConfig>()?;
    m.add_class::<RabbitMQConfig>()?;

    m.add_class::<SpcServerRecord>()?;
    m.add_class::<PsiServerRecord>()?;
    m.add_class::<CustomMetricServerRecord>()?;
    m.add_class::<ServerRecord>()?;
    m.add_class::<ServerRecords>()?;
    m.add_class::<RecordType>()?;

    m.add_class::<Feature>()?;
    m.add_class::<Features>()?;
    m.add_class::<PsiFeatureQueue>()?;
    m.add_class::<SpcFeatureQueue>()?;

    Ok(())
}
