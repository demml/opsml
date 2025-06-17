use crate::error::CliError;
use opsml_colors::Colorize;
use opsml_toml::PyProjectToml;

use pyo3::prelude::*;
use std::path::PathBuf;

#[pyfunction]
#[pyo3(signature = (path=None, toml_name=None))]
pub fn validate_project(path: Option<PathBuf>, toml_name: Option<&str>) -> Result<(), CliError> {
    PyProjectToml::load(path.as_deref(), toml_name)?;
    println!("{}", Colorize::green("Opsml Project is valid!"));

    Ok(())
}
