use opsml_interfaces::{
    CatBoostModel, DataProcessor, HuggingFaceModel, HuggingFaceORTModel, HuggingFaceOnnxArgs,
    HuggingFaceTask, LightGBMModel, LightningModel, ModelInterface, ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata, ModelInterfaceType, ModelType, OnnxSession, SklearnModel, TaskType,
    TensorFlowModel, TorchModel, XGBoostModel,
};

use pyo3::prelude::*;

#[pymodule]
pub fn model(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_interfaces
    m.add_class::<HuggingFaceOnnxArgs>()?;
    m.add_class::<HuggingFaceORTModel>()?;
    m.add_class::<TaskType>()?;

    // helper types
    m.add_class::<DataProcessor>()?;
    m.add_class::<OnnxSession>()?;
    m.add_class::<ModelInterfaceType>()?;
    m.add_class::<ModelType>()?;
    m.add_class::<HuggingFaceTask>()?;

    // Model Interface
    m.add_class::<ModelInterfaceMetadata>()?;
    m.add_class::<ModelInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterface>()?;
    m.add_class::<SklearnModel>()?;
    m.add_class::<LightGBMModel>()?;
    m.add_class::<XGBoostModel>()?;
    m.add_class::<TorchModel>()?;
    m.add_class::<LightningModel>()?;
    m.add_class::<HuggingFaceModel>()?;
    m.add_class::<CatBoostModel>()?;
    m.add_class::<TensorFlowModel>()?;

    Ok(())
}
