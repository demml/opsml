use crate::model::torch::{TorchOnnxArgs, TorchSaveArgs};
use crate::Feature;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TorchInterfaceMetadata {
    #[pyo3(get)]
    pub task_type: String,
    #[pyo3(get)]
    pub model_type: String,
    #[pyo3(get)]
    pub data_type: String,
    #[pyo3(get)]
    pub modelcard_uid: String,
    #[pyo3(get)]
    pub feature_map: HashMap<String, Feature>,
    #[pyo3(get)]
    pub sample_data_interface_type: String,
    #[pyo3(get)]
    pub preprocessor_name: String,
    #[pyo3(get)]
    pub onnx_args: Option<TorchOnnxArgs>,
    #[pyo3(get)]
    pub save_args: TorchSaveArgs,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl TorchInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, onnx_args=None, save_args=None, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        onnx_args: Option<TorchOnnxArgs>,
        save_args: Option<TorchSaveArgs>,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        TorchInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            save_args: save_args.unwrap_or(TorchSaveArgs::new(None)),
            onnx_args,
            metadata: metadata.unwrap_or_default(),
        }
    }
}
