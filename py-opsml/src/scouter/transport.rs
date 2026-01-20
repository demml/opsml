use pyo3::prelude::*;
use scouter_client::*;

pub fn add_transport_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<KafkaConfig>()?;
    m.add_class::<RabbitMQConfig>()?;
    m.add_class::<RedisConfig>()?;
    m.add_class::<HttpConfig>()?;
    m.add_class::<GrpcConfig>()?;
    Ok(())
}
