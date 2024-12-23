use crate::cards::model::{HuggingFaceORTModel, TorchOnnxArgs, TorchSaveArgs};
use crate::shared::{CommonKwargs, PyHelperFuncs};
use crate::Feature;
use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelInterfaceSaveMetadata {
    #[pyo3(get)]
    pub trained_model_uri: String,

    #[pyo3(get)]
    pub preprocessor_uri: Option<String>,

    #[pyo3(get)]
    pub preprocessor_name: Option<String>,

    #[pyo3(get)]
    pub sample_data_uri: String,

    #[pyo3(get)]
    pub onnx_model_uri: Option<String>,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,
}

#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (trained_model_uri, sample_data_uri,  preprocessor_uri=None, preprocessor_name=None, onnx_model_uri=None, extra_metadata=None))]
    pub fn new(
        trained_model_uri: String,
        sample_data_uri: String,
        preprocessor_uri: Option<String>,
        preprocessor_name: Option<String>,
        onnx_model_uri: Option<String>,
        extra_metadata: Option<HashMap<String, String>>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            trained_model_uri,
            sample_data_uri,
            preprocessor_uri,
            preprocessor_name,
            onnx_model_uri,
            extra_metadata: extra_metadata.unwrap_or_default(),
        }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelInterfaceMetadata {
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
    pub save_metadata: ModelInterfaceSaveMetadata,
    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,
}

#[pymethods]
impl ModelInterfaceMetadata {
    #[new]
    #[pyo3(signature = (interface, save_metadata, extra_metadata=None))]
    fn new(
        interface: &Bound<'_, PyAny>,
        save_metadata: ModelInterfaceSaveMetadata,
        extra_metadata: Option<HashMap<String, String>>,
    ) -> PyResult<Self> {
        let task_type: String = interface
            .getattr("task_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get task_type: {}", e)))?
            .to_string();

        let model_type: String = interface
            .getattr("model_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get task_type: {}", e)))?
            .to_string();

        let data_type: String = interface
            .getattr("data_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get task_type: {}", e)))?
            .to_string();

        let modelcard_uid: String = interface
            .getattr("modelcard_uid")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get task_type: {}", e)))?
            .to_string();

        let feature_map: HashMap<String, Feature> = interface
            .getattr("feature_map")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get feature_map: {}", e)))?
            .extract()?;

        let sample_data_interface_type: String = interface
            .getattr("sample_data_interface_type")
            .map_err(|e| {
                OpsmlError::new_err(format!("Failed to get sample_data_interface_type: {}", e))
            })?
            .to_string();

        Ok(ModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            save_metadata,
            extra_metadata: extra_metadata.unwrap_or_default(),
        })
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SklearnModelInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl SklearnModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        SklearnModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CatBoostModelInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl CatBoostModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        CatBoostModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

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
    pub feature_map: HashMap<String, Feature>,
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
        feature_map: HashMap<String, Feature>,
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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LightGBMModelInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl LightGBMModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        LightGBMModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LightningInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl LightningInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, onnx_args=None, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        onnx_args: Option<TorchOnnxArgs>,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        LightningInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            onnx_args,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

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

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TensorFlowInterfaceMetadata {
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
    pub preprocessor_name: String,
    #[pyo3(get)]
    pub sample_data_interface_type: String,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl TensorFlowInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, preprocessor_name, sample_data_interface_type, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        preprocessor_name: String,
        sample_data_interface_type: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        TensorFlowInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            preprocessor_name,
            sample_data_interface_type,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct VowpalWabbitInterfaceMetadata {
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
    pub arguments: String,
    #[pyo3(get)]
    pub sample_data_interface_type: String,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl VowpalWabbitInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, arguments, sample_data_interface_type, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        arguments: String,
        sample_data_interface_type: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        VowpalWabbitInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            arguments,
            sample_data_interface_type,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct XGBoostModelInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl XGBoostModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: HashMap<String, Feature>,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        XGBoostModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum ModelSaveMetadata {
    Base(ModelInterfaceSaveMetadata),
}

#[pymethods]
impl ModelSaveMetadata {
    #[new]
    #[pyo3(signature = (save_args))]
    pub fn new(save_args: &Bound<'_, PyAny>) -> PyResult<Self> {
        if save_args.is_instance_of::<ModelInterfaceSaveMetadata>() {
            let args: ModelInterfaceSaveMetadata = save_args.extract().map_err(|e| {
                OpsmlError::new_err(format!("Failed to extract ModelInterfaceArgs: {}", e))
            })?;
            Ok(ModelSaveMetadata::Base(args))
        } else {
            Err(OpsmlError::new_err("Invalid ModelInterfaceArgs type"))
        }
    }

    pub fn type_name(&self) -> &str {
        match self {
            ModelSaveMetadata::Base(_) => "Base",
        }
    }
}
