use pyo3::prelude::*;
use scouter_client::{DatasetClient, DatasetProducer, QueryResult, TableConfig, WriteConfig};

pub fn add_dataset_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DatasetClient>()?;
    m.add_class::<DatasetProducer>()?;
    m.add_class::<TableConfig>()?;
    m.add_class::<WriteConfig>()?;
    m.add_class::<QueryResult>()?;
    Ok(())
}
