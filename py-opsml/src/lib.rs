pub mod card;
pub mod core;
pub mod data;
pub mod experiment;
pub mod model;
pub mod potato_head;
pub mod scouter;
pub mod test;

use pyo3::prelude::*;
use pyo3::wrap_pymodule;

#[pymodule]
fn opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // integrations
    m.add_wrapped(wrap_pymodule!(scouter::scouter))?;
    m.add_wrapped(wrap_pymodule!(potato_head::potato_head))?;

    // core
    m.add_wrapped(wrap_pymodule!(core::core))?;
    m.add_wrapped(wrap_pymodule!(data::data))?;
    m.add_wrapped(wrap_pymodule!(model::model))?;
    m.add_wrapped(wrap_pymodule!(card::card))?;
    m.add_wrapped(wrap_pymodule!(experiment::experiment))?;

    // test
    m.add_wrapped(wrap_pymodule!(test::test))?;
    Ok(())
}
