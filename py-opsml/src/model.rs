use opsml_interfaces::{
    CatBoostModelInterfaceMetadata, HuggingFaceModelInterfaceMetadata, HuggingFaceORTModel,
    HuggingFaceOnnxArgs, HuggingFaceOnnxSaveArgs, LightGBMModelInterfaceMetadata,
    LightningInterfaceMetadata, ModelDataInterfaceSaveMetadata, ModelInterfaceMetadata,
    ModelInterfaceType, ModelSaveMetadata, SklearnModelInterfaceMetadata,
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

    // Model Interface
    m.add_class::<ModelDataInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterfaceMetadata>()?;

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
    m.add_class::<ModelSaveMetadata>()?;
    m.add_class::<ModelDataInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterfaceType>()?;

    Ok(())
}
