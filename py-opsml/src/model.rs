use opsml_interfaces::{
    CatBoostModel, DataProcessor, HuggingFaceModel, HuggingFaceORTModel, HuggingFaceOnnxArgs,
    HuggingFaceTask, LightGBMModel, LightningModel, ModelInterface, ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata, ModelLoadKwargs, ModelSaveKwargs, OnnxModel, OnnxSchema,
    OnnxSession, ProcessorType, SklearnModel, TensorFlowModel, TorchModel, XGBoostModel,
};
use opsml_types::{ModelInterfaceType, ModelType, TaskType};

use pyo3::prelude::*;

#[pymodule]
pub fn model(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // opsml_interfaces
    m.add_class::<HuggingFaceOnnxArgs>()?;
    m.add_class::<HuggingFaceORTModel>()?;

    // helper types
    m.add_class::<DataProcessor>()?;
    m.add_class::<OnnxSession>()?;
    m.add_class::<HuggingFaceTask>()?;
    m.add_class::<ModelSaveKwargs>()?;
    m.add_class::<ModelLoadKwargs>()?;

    // Model Interface
    m.add_class::<ModelInterfaceMetadata>()?;
    m.add_class::<ModelInterfaceSaveMetadata>()?;
    m.add_class::<ModelInterface>()?;
    m.add_class::<TaskType>()?;
    m.add_class::<ModelInterfaceType>()?;
    m.add_class::<ModelType>()?;

    m.add_class::<SklearnModel>()?;
    m.add_class::<LightGBMModel>()?;
    m.add_class::<XGBoostModel>()?;
    m.add_class::<TorchModel>()?;
    m.add_class::<LightningModel>()?;
    m.add_class::<HuggingFaceModel>()?;
    m.add_class::<CatBoostModel>()?;
    m.add_class::<TensorFlowModel>()?;
    m.add_class::<OnnxModel>()?;

    // Feature
    m.add_class::<OnnxSchema>()?;

    // Processor
    m.add_class::<ProcessorType>()?;

    Ok(())
}
