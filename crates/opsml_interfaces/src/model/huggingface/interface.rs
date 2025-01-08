use crate::model::huggingface::HuggingFaceORTModel;
use crate::SchemaFeature;
use opsml_types::CommonKwargs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct HuggingFaceOnnxSaveArgs {
    ort_type: HuggingFaceORTModel,
    provider: String,
    quantize: bool,
}
#[pymethods]
impl HuggingFaceOnnxSaveArgs {
    #[new]
    pub fn new(ort_type: HuggingFaceORTModel, provider: String, quantize: bool) -> Self {
        HuggingFaceOnnxSaveArgs {
            ort_type,
            provider,
            quantize,
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct HuggingFaceModelInterfaceMetadata {
    #[pyo3(get)]
    pub task_type: String,
    #[pyo3(get)]
    pub model_type: String,
    #[pyo3(get)]
    pub data_type: String,
    #[pyo3(get)]
    pub modelcard_uid: String,
    #[pyo3(get)]
    pub feature_map: HashMap<String, SchemaFeature>,
    #[pyo3(get)]
    pub sample_data_interface_type: String,
    #[pyo3(get)]
    pub preprocessor_name: String,
    #[pyo3(get)]
    pub is_pipeline: bool,
    #[pyo3(get)]
    pub backend: CommonKwargs,
    #[pyo3(get)]
    pub onnx_args: HuggingFaceOnnxSaveArgs,
    #[pyo3(get)]
    pub tokenizer_name: String,
    #[pyo3(get)]
    pub feature_extractor_name: String,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl HuggingFaceModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, is_pipeline, backend, onnx_args, tokenizer_name, feature_extractor_name, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, SchemaFeature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        is_pipeline: bool,
        backend: CommonKwargs,
        onnx_args: HuggingFaceOnnxSaveArgs,
        tokenizer_name: String,
        feature_extractor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        HuggingFaceModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            is_pipeline,
            backend,
            onnx_args,
            tokenizer_name,
            feature_extractor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}
