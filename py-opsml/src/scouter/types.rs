use pyo3::prelude::*;
use scouter_client::*;

#[pymodule]
pub fn types(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DriftType>()?;
    m.add_class::<CommonCrons>()?;
    m.add_class::<DataType>()?;
    m.add("ScouterError", m.py().get_type::<PyScouterError>())?;

    Ok(())
}
