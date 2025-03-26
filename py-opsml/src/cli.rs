use opsml_cli::run_cli;
use pyo3::prelude::*;
use std::env;

#[pyfunction]
pub fn run_opsml_cli() -> anyhow::Result<()> {
    let args: Vec<String> = env::args().collect();
    run_cli(args)
}
