pub mod card;
pub mod cli;
pub mod core;
pub mod data;
pub mod experiment;
pub mod model;
pub mod potato_head;
pub mod scouter;
pub mod test;
pub mod types;

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

    // types
    m.add_wrapped(wrap_pymodule!(types::types))?;

    // test
    m.add_wrapped(wrap_pymodule!(test::test))?;

    // cli
    m.add_wrapped(wrap_pymodule!(cli::cli))?;
    //m.add_function(wrap_pyfunction!(cli::run_opsml_cli, m)?)?;
    Ok(())
}
