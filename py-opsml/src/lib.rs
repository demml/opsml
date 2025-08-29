pub mod app;
pub mod card;
pub mod cli;
pub mod data;
pub mod experiment;
pub mod llm;
pub mod logging;
pub mod mocks;
pub mod model;
pub mod scouter;
pub mod types;

use pyo3::prelude::*;
use pyo3::wrap_pymodule;

#[pyfunction]
pub fn get_opsml_version() -> PyResult<String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

#[pymodule]
fn opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // integrations
    m.add_wrapped(wrap_pymodule!(scouter::scouter))?;
    m.add_wrapped(wrap_pymodule!(llm::llm))?;

    m.add_wrapped(wrap_pymodule!(data::data))?;
    m.add_wrapped(wrap_pymodule!(model::model))?;
    m.add_wrapped(wrap_pymodule!(card::card))?;
    m.add_wrapped(wrap_pymodule!(experiment::experiment))?;
    m.add_wrapped(wrap_pymodule!(app::app))?;

    // types
    m.add_wrapped(wrap_pymodule!(types::types))?;

    // logging
    m.add_wrapped(wrap_pymodule!(logging::logging))?;

    // test
    m.add_wrapped(wrap_pymodule!(mocks::mock))?;

    // cli
    m.add_wrapped(wrap_pymodule!(cli::cli))?;
    //m.add_function(wrap_pyfunction!(cli::run_opsml_cli, m)?)?;

    m.add_function(wrap_pyfunction!(get_opsml_version, m)?)?;
    Ok(())
}
