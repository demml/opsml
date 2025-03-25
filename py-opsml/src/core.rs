use opsml_error::error::OpsmlError;
use opsml_interfaces::{base::ExtraMetadata, Feature, FeatureSchema, OnnxSchema};
use opsml_semver::VersionType;
use opsml_types::{CommonKwargs, InterfaceType, SaveName, SaverPath, StorageType, Suffix};
use pyo3::prelude::*;
use rusty_logging::{LogLevel, LoggingConfig, RustyLogger};

#[pymodule]
pub fn core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    m.add_class::<LogLevel>()?;
    m.add_class::<LoggingConfig>()?;
    m.add_class::<RustyLogger>()?;

    // opsml_errors
    m.add("OpsmlError", m.py().get_type::<OpsmlError>())?;

    m.add_class::<ExtraMetadata>()?;

    // opsml_types
    m.add_class::<CommonKwargs>()?;
    m.add_class::<SaveName>()?;
    m.add_class::<Suffix>()?;
    m.add_class::<InterfaceType>()?;
    m.add_class::<SaverPath>()?;
    m.add_class::<FeatureSchema>()?;
    m.add_class::<Feature>()?;
    m.add_class::<OnnxSchema>()?;

    // opsml_semver
    m.add_class::<VersionType>()?;

    // opsml_storage
    m.add_class::<StorageType>()?;

    Ok(())
}
