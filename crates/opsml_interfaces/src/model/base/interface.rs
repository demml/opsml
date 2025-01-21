use crate::model::{SampleData, TaskType};
use crate::types::FeatureSchema;
use crate::Feature;
use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tracing::warn;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelDataInterfaceSaveMetadata {
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
impl ModelDataInterfaceSaveMetadata {
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
        ModelDataInterfaceSaveMetadata {
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
    pub save_metadata: ModelDataInterfaceSaveMetadata,
    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,
}

#[pymethods]
impl ModelInterfaceMetadata {
    #[new]
    #[pyo3(signature = (interface, save_metadata, extra_metadata=None))]
    fn new(
        interface: &Bound<'_, PyAny>,
        save_metadata: ModelDataInterfaceSaveMetadata,
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

#[pyclass(subclass)]
pub struct ModelInterface {
    #[pyo3(get)]
    pub model: PyObject,

    #[pyo3(get, set)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub task_type: TaskType,

    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    pub sample_data: SampleData,
}

#[pymethods]
impl ModelInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=TaskType::Other, schema=None,))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: TaskType,
        schema: Option<FeatureSchema>,
    ) -> PyResult<Self> {
        let model = match model {
            Some(model) => model.into_py_any(py)?,
            None => py.None(),
        };

        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => SampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {}", e);
                SampleData::default()
            }),
            None => SampleData::default(),
        };

        let schema = schema.unwrap_or_default();

        Ok(ModelInterface {
            model,
            data_type: sample_data.get_data_type(),
            task_type,
            schema,
            sample_data,
        })
    }

    #[getter]
    pub fn get_sample_data(&self, py: Python<'_>) -> PyResult<PyObject> {
        self.sample_data.get_data(py)
    }

    #[setter]
    pub fn set_sample_data(&mut self, sample_data: &Bound<'_, PyAny>) -> PyResult<()> {
        self.sample_data = SampleData::new(sample_data)?;
        Ok(())
    }
}
