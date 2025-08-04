use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn queue(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<KafkaConfig>()?;
    m.add_class::<RabbitMQConfig>()?;
    m.add_class::<RedisConfig>()?;

    m.add_class::<SpcServerRecord>()?;
    m.add_class::<PsiServerRecord>()?;
    m.add_class::<CustomMetricServerRecord>()?;
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
