use opsml_interfaces::{
    CatBoostModelInterfaceMetadata, HuggingFaceModelInterfaceMetadata, HuggingFaceORTModel,
    HuggingFaceOnnxArgs, HuggingFaceOnnxSaveArgs, LightGBMModelInterfaceMetadata,
    LightningInterfaceMetadata, ModelInterface, ModelInterfaceMetadata, ModelInterfaceType,
    OnnxSession, SklearnModel, SklearnModelInterfaceMetadata, TaskType,
    TensorFlowInterfaceMetadata, TorchInterfaceMetadata, TorchOnnxArgs, TorchSaveArgs,
    VowpalWabbitInterfaceMetadata, XGBoostModelInterfaceMetadata,
};

use pyo3::prelude::*;

#[pymodule]
pub fn model(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_interfaces
    m.add_class::<HuggingFaceOnnxArgs>()?;
    m.add_class::<HuggingFaceORTModel>()?;
    m.add_class::<HuggingFaceOnnxSaveArgs>()?;
    m.add_class::<TorchOnnxArgs>()?;
    m.add_class::<TorchSaveArgs>()?;
    m.add_class::<TaskType>()?;

    // Model Interface
    m.add_class::<ModelInterfaceMetadata>()?;
    m.add_class::<ModelInterface>()?;

    // Model Interface args
    m.add_class::<CatBoostModelInterfaceMetadata>()?;
    m.add_class::<HuggingFaceModelInterfaceMetadata>()?;
    m.add_class::<LightGBMModelInterfaceMetadata>()?;
    m.add_class::<LightningInterfaceMetadata>()?;
    m.add_class::<SklearnModelInterfaceMetadata>()?;
    m.add_class::<TensorFlowInterfaceMetadata>()?;
    m.add_class::<TorchInterfaceMetadata>()?;
    m.add_class::<VowpalWabbitInterfaceMetadata>()?;
    m.add_class::<XGBoostModelInterfaceMetadata>()?;
    m.add_class::<ModelInterfaceType>()?;
    m.add_class::<SklearnModel>()?;
    m.add_class::<OnnxSession>()?;

    Ok(())
}
