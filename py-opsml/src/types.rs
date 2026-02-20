use opsml_interfaces::{
    DriftArgs, DriftProfileMap, ExtraMetadata, Feature, FeatureSchema, PromptSaveKwargs,
};
use opsml_semver::VersionType;
use opsml_types::{CommonKwargs, DataType, DriftProfileUri, SaveName, SaverPath, Suffix};
use pyo3::prelude::*;

pub fn add_types_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CommonKwargs>()?;
    m.add_class::<SaveName>()?;
    m.add_class::<Suffix>()?;
    m.add_class::<VersionType>()?;
    m.add_class::<SaverPath>()?;
    m.add_class::<DriftProfileUri>()?;
    m.add_class::<DriftArgs>()?;
    m.add_class::<DriftProfileMap>()?;

    // common types
    m.add_class::<DataType>()?;
    m.add_class::<Feature>()?;
    m.add_class::<ExtraMetadata>()?;
    m.add_class::<FeatureSchema>()?;
    m.add_class::<PromptSaveKwargs>()?;

    Ok(())
}
