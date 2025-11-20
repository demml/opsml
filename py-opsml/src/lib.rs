pub mod app;
pub mod card;
pub mod cli;
pub mod data;
pub mod evaluate;
pub mod experiment;
pub mod genai;
pub mod logging;
pub mod mocks;
pub mod model;
pub mod scouter;
pub mod types;

use pyo3::prelude::*;

#[pyfunction]
pub fn get_opsml_version() -> PyResult<String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

#[pymodule]
fn _opsml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_opsml_version, m)?)?;

    // integrations
    scouter::add_scouter_module(m)?;
    genai::add_genai_module(m)?;

    cli::add_cli_module(m)?;
    card::add_card_module(m)?;
    app::add_app_module(m)?;
    data::add_data_module(m)?;
    model::add_model_module(m)?;
    evaluate::add_evaluate_module(m)?;
    experiment::add_experiment_module(m)?;
    types::add_types_module(m)?;
    logging::add_logging_module(m)?;
    mocks::add_mocks_module(m)?;

    Ok(())
}
