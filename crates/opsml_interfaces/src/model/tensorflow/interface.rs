use crate::Feature;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

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
