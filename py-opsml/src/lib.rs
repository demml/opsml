#[cfg(feature = "server")]
use opsml_registry::RegistryTestHelper;

use opsml_error::error::OpsmlError;
use opsml_logging::logging::OpsmlLogger;
use opsml_registry::PyCardRegistry;
use opsml_settings::config::OpsmlConfig;
use opsml_types::cards::model::{
    CatBoostModelInterfaceMetadata, HuggingFaceModelInterfaceMetadata,
    LightGBMModelInterfaceMetadata, LightningInterfaceMetadata, ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata, ModelSaveMetadata, SklearnModelInterfaceMetadata,
    TensorFlowInterfaceMetadata, TorchInterfaceMetadata, VowpalWabbitInterfaceMetadata,
    XGBoostModelInterfaceMetadata,
};
use opsml_types::cards::{
    DataSchema, Description, Feature, HuggingFaceORTModel, HuggingFaceOnnxArgs,
    HuggingFaceOnnxSaveArgs, OnnxSchema, RegistryType, TorchOnnxArgs, TorchSaveArgs, VersionType,
};
use opsml_types::shared::{CommonKwargs, SaveName, Suffix};
use opsml_types::{Card, CardInfo, CardList, LogLevel, ModelInterfaceType};
use pyo3::prelude::*;

#[pymodule]
fn _opsml(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    // logging
    _m.add_class::<LogLevel>()?;
    _m.add_class::<OpsmlLogger>()?;

    // errors
    _m.add("OpsmlError", _m.py().get_type::<OpsmlError>())?;

    // config
    _m.add_class::<OpsmlConfig>()?;

    // shared
    _m.add_class::<CommonKwargs>()?;
    _m.add_class::<SaveName>()?;
    _m.add_class::<Suffix>()?;
    _m.add_class::<RegistryType>()?;

    // cards (types that are used across cards)
    _m.add_class::<HuggingFaceOnnxArgs>()?;
    _m.add_class::<HuggingFaceORTModel>()?;
    _m.add_class::<HuggingFaceOnnxSaveArgs>()?;
    _m.add_class::<TorchOnnxArgs>()?;
    _m.add_class::<TorchSaveArgs>()?;
    _m.add_class::<Feature>()?;
    _m.add_class::<Description>()?;
    _m.add_class::<VersionType>()?;
    _m.add_class::<DataSchema>()?;
    _m.add_class::<OnnxSchema>()?;
    _m.add_class::<CardInfo>()?;
    _m.add_class::<Card>()?;
    _m.add_class::<CardList>()?;

    // Model Interface
    _m.add_class::<ModelInterfaceSaveMetadata>()?;
    _m.add_class::<ModelInterfaceMetadata>()?;

    // Model Interface args
    _m.add_class::<CatBoostModelInterfaceMetadata>()?;
    _m.add_class::<HuggingFaceModelInterfaceMetadata>()?;
    _m.add_class::<LightGBMModelInterfaceMetadata>()?;
    _m.add_class::<LightningInterfaceMetadata>()?;
    _m.add_class::<SklearnModelInterfaceMetadata>()?;
    _m.add_class::<TensorFlowInterfaceMetadata>()?;
    _m.add_class::<TorchInterfaceMetadata>()?;
    _m.add_class::<VowpalWabbitInterfaceMetadata>()?;
    _m.add_class::<XGBoostModelInterfaceMetadata>()?;
    _m.add_class::<ModelSaveMetadata>()?;
    _m.add_class::<ModelInterfaceSaveMetadata>()?;

    // registry
    _m.add_class::<PyCardRegistry>()?;

    // model interface
    _m.add_class::<ModelInterfaceType>()?;

    #[cfg(feature = "server")]
    _m.add_class::<RegistryTestHelper>()?;

    Ok(())
}
