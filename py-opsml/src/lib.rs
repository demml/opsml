pub mod card;
pub mod core;
pub mod data;
pub mod model;
pub mod scouter;
pub mod storage;

use pyo3::prelude::*;
use pyo3::wrap_pymodule;

#[pymodule]
fn opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_wrapped(wrap_pymodule!(scouter::scouter))?;
    m.add_wrapped(wrap_pymodule!(core::core))?;
    m.add_wrapped(wrap_pymodule!(data::data))?;
    m.add_wrapped(wrap_pymodule!(model::model))?;
    m.add_wrapped(wrap_pymodule!(card::card))?;
    m.add_wrapped(wrap_pymodule!(storage::storage))?;

    Ok(())
}
