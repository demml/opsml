use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData};
use crate::model::{InterfaceDataType, SampleData, TaskType};
use crate::types::FeatureSchema;
use crate::Feature;
use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PySlice;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

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

pub struct ModelInterfaceDataHelper {}

impl ModelInterfaceDataHelper {
    pub fn get_sample_data<'py>(data: &Bound<'py, PyAny>) -> PyResult<PyObject> {
        // get python interpreter
        let py = data.py();

        // check if data is instance of DataInterface
        if data.is_instance_of::<DataInterface>() {
            // extract data
            // get slice of data (data.data[0:1])
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_data = data.getattr("data")?.get_item(slice)?;
            // set interface data to sliced data
            data.setattr("data", sliced_data)?;

            return Ok(data.clone().unbind());
        } else {
            // attempt to get interface from data
            let interface = ModelInterfaceDataHelper::get_interface_for_sample(data)?;

            if let Some(interface) = interface {
                // get sample data

                return Ok(interface);
            } else {
                return Err(OpsmlError::new_err("Failed to get interface type"));
            }
        }
    }

    pub fn get_interface_for_sample<'py>(data: &Bound<'py, PyAny>) -> PyResult<Option<PyObject>> {
        let py = data.py();
        let class = data.getattr("__class__")?;
        let module = class.getattr("__module__")?.str()?.to_string();
        let name = class.getattr("__name__")?.str()?.to_string();
        let full_class_name = format!("{}.{}", module, name);

        let interface_type = InterfaceDataType::from_module_name(&full_class_name).ok();

        // if interface_type is not None, match is to the DataInterfaces and return the interface
        if let Some(interface_type) = interface_type {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_data = data.get_item(slice)?;
            match interface_type {
                InterfaceDataType::Pandas => {
                    let interface =
                        PandasData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    return Ok(Some(bound));
                }
                InterfaceDataType::Polars => {
                    let interface =
                        PolarsData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    return Ok(Some(bound));
                }
                InterfaceDataType::Numpy => {
                    let interface =
                        NumpyData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    return Ok(Some(bound));
                }
                InterfaceDataType::Arrow => {
                    let interface =
                        PandasData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    return Ok(Some(bound));
                }
            }
        } else {
            return Ok(None);
        }
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
