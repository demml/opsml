use opsml_error::error::OpsmlError;
use opsml_logging::logging::{LogLevel, OpsmlLogger};
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;

use opsml_cards::{DataSchema, OnnxSchema};
use opsml_interfaces::{Feature, FeatureSchema};
use opsml_types::{
    CommonKwargs, DataType, InterfaceType, RegistryType, SaveName, SaverPath, Suffix,
};
use opsml_utils::FileUtils;
use pyo3::prelude::*;

#[pymodule]
pub fn core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<LogLevel>()?;
    m.add_class::<OpsmlLogger>()?;

    // opsml_errors
    m.add("OpsmlError", m.py().get_type::<OpsmlError>())?;

    // opsml_settings
    m.add_class::<OpsmlConfig>()?;

    // opsml_types
    m.add_class::<CommonKwargs>()?;
    m.add_class::<SaveName>()?;
    m.add_class::<Suffix>()?;
    m.add_class::<RegistryType>()?;
    m.add_class::<DataType>()?;
    m.add_class::<InterfaceType>()?;
    m.add_class::<SaverPath>()?;
    m.add_class::<FeatureSchema>()?;
    m.add_class::<Feature>()?;
    m.add_class::<DataSchema>()?;
    m.add_class::<OnnxSchema>()?;

    // opsml_semver
    m.add_class::<VersionType>()?;

    // opsml_utils
    m.add_class::<FileUtils>()?;

    Ok(())
}
