use opsml_cards::{CardInfo, DataSchema, Description, OnnxSchema};
use opsml_contracts::{Card, CardList};
use opsml_error::error::OpsmlError;
use opsml_interfaces::{
    data::{
        ColType, ColValType, ColumnSplit, Data, DataInterface, DataSplit, DataSplits, DataSplitter,
        DependentVars, IndiceSplit, Inequality, SqlLogic, StartStopSplit,
    },
    CatBoostModelInterfaceMetadata, Feature, FeatureMap, HuggingFaceModelInterfaceMetadata,
    HuggingFaceORTModel, HuggingFaceOnnxArgs, HuggingFaceOnnxSaveArgs,
    LightGBMModelInterfaceMetadata, LightningInterfaceMetadata, ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata, ModelInterfaceType, ModelSaveMetadata,
    SklearnModelInterfaceMetadata, TensorFlowInterfaceMetadata, TorchInterfaceMetadata,
    TorchOnnxArgs, TorchSaveArgs, VowpalWabbitInterfaceMetadata, XGBoostModelInterfaceMetadata,
};
use opsml_logging::logging::{LogLevel, OpsmlLogger};
use opsml_registry::PyCardRegistry;
#[cfg(feature = "server")]
use opsml_registry::RegistryTestHelper;
use opsml_semver::VersionType;
use opsml_settings::config::OpsmlConfig;

use opsml_types::{CommonKwargs, DataType, RegistryType, SaveName, Suffix};
use opsml_utils::FileUtils;
use pyo3::prelude::*;

#[pymodule]
fn _opsml(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_logging
    _m.add_class::<LogLevel>()?;
    _m.add_class::<OpsmlLogger>()?;

    // opsml_errors
    _m.add("OpsmlError", _m.py().get_type::<OpsmlError>())?;

    // opsml_settings
    _m.add_class::<OpsmlConfig>()?;

    // opsml_types
    _m.add_class::<CommonKwargs>()?;
    _m.add_class::<SaveName>()?;
    _m.add_class::<Suffix>()?;
    _m.add_class::<RegistryType>()?;
    _m.add_class::<DataType>()?;

    // opsml_semver
    _m.add_class::<VersionType>()?;

    // opsml_utils
    _m.add_class::<FileUtils>()?;

    // opsml_interfaces
    _m.add_class::<HuggingFaceOnnxArgs>()?;
    _m.add_class::<HuggingFaceORTModel>()?;
    _m.add_class::<HuggingFaceOnnxSaveArgs>()?;
    _m.add_class::<TorchOnnxArgs>()?;
    _m.add_class::<TorchSaveArgs>()?;
    _m.add_class::<Feature>()?;
    _m.add_class::<FeatureMap>()?;
    _m.add_class::<Description>()?;
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
    _m.add_class::<ModelInterfaceType>()?;

    // data_splitter
    _m.add_class::<DataSplit>()?;
    _m.add_class::<Data>()?;
    _m.add_class::<ColumnSplit>()?;
    _m.add_class::<StartStopSplit>()?;
    _m.add_class::<IndiceSplit>()?;
    _m.add_class::<ColType>()?;
    _m.add_class::<ColValType>()?;
    _m.add_class::<DataSplitter>()?;
    _m.add_class::<Inequality>()?;
    _m.add_class::<DependentVars>()?;
    _m.add_class::<SqlLogic>()?;
    _m.add_class::<DataSplits>()?;

    // data_interface
    _m.add_class::<DataInterface>()?;

    // opsml_registry
    _m.add_class::<PyCardRegistry>()?;

    #[cfg(feature = "server")]
    _m.add_class::<RegistryTestHelper>()?;

    Ok(())
}
