use opsml_interfaces::{
    CatBoostModelInterfaceMetadata, DataProcessor, HuggingFaceModelInterfaceMetadata,
    HuggingFaceORTModel, HuggingFaceOnnxArgs, HuggingFaceOnnxSaveArgs, LightGBMModel,
    LightGBMModelInterfaceMetadata, LightningModel, LoadKwargs, ModelInterface,
    ModelInterfaceMetadata, ModelInterfaceSaveMetadata, ModelInterfaceType, ModelType, OnnxSession,
    SaveKwargs, SklearnModel, SklearnModelInterfaceMetadata, TaskType, TensorFlowInterfaceMetadata,
    TorchModel, VowpalWabbitInterfaceMetadata, XGBoostModel, XGBoostModelInterfaceMetadata,
};

use pyo3::prelude::*;

#[pymodule]
pub fn model(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_interfaces
    m.add_class::<HuggingFaceOnnxArgs>()?;
    m.add_class::<HuggingFaceORTModel>()?;
    m.add_class::<HuggingFaceOnnxSaveArgs>()?;
    m.add_class::<TaskType>()?;

    // helper types
    m.add_class::<DataProcessor>()?;
    m.add_class::<OnnxSession>()?;
    m.add_class::<SaveKwargs>()?;
    m.add_class::<LoadKwargs>()?;
    m.add_class::<ModelInterfaceType>()?;
    m.add_class::<ModelType>()?;

    // Model Interface
    m.add_class::<ModelInterfaceMetadata>()?;
    m.add_class::<ModelInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterface>()?;
    m.add_class::<SklearnModel>()?;
    m.add_class::<LightGBMModel>()?;
    m.add_class::<XGBoostModel>()?;
    m.add_class::<TorchModel>()?;
    m.add_class::<LightningModel>()?;

    // Model Interface args
    m.add_class::<CatBoostModelInterfaceMetadata>()?;
    m.add_class::<HuggingFaceModelInterfaceMetadata>()?;
    m.add_class::<LightGBMModelInterfaceMetadata>()?;
    m.add_class::<SklearnModelInterfaceMetadata>()?;
    m.add_class::<TensorFlowInterfaceMetadata>()?;
    m.add_class::<VowpalWabbitInterfaceMetadata>()?;
    m.add_class::<XGBoostModelInterfaceMetadata>()?;

    Ok(())
}
