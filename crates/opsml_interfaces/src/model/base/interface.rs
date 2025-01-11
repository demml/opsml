use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::model::onnx::OnnxModelConverter;
use crate::model::{SampleData, TaskType};
use crate::types::{Feature, FeatureSchema, ModelInterfaceType, ModelType};
use opsml_error::error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::warn;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelInterfaceSaveMetadata {
    #[pyo3(get)]
    pub model_uri: PathBuf,

    #[pyo3(get)]
    pub preprocessor_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub preprocessor_name: Option<PathBuf>,

    #[pyo3(get)]
    pub sample_data_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub onnx_model_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,
}

#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (model_uri, sample_data_uri,  preprocessor_uri=None, preprocessor_name=None, onnx_model_uri=None, extra_metadata=HashMap::new()))]
    pub fn new(
        model_uri: PathBuf,
        sample_data_uri: Option<PathBuf>,
        preprocessor_uri: Option<PathBuf>,
        preprocessor_name: Option<PathBuf>,
        onnx_model_uri: Option<PathBuf>,
        extra_metadata: HashMap<String, String>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            model_uri,
            sample_data_uri,
            preprocessor_uri,
            preprocessor_name,
            onnx_model_uri,
            extra_metadata,
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

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub model_interface_type: ModelInterfaceType,

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
        // Extract the sample data
        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => SampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {}", e);
                SampleData::default()
            }),
            None => SampleData::default(),
        };

        // Extract the schema if it exists
        let schema = schema.unwrap_or_default();

        // Determing model_type
        let model_type = if let Some(model) = model {
            ModelType::from_pyobject(model)
        } else {
            ModelType::Unknown
        };

        // Convert the model to a PyObject for storing in struct
        let model = match model {
            Some(model) => model.into_py_any(py)?,
            None => py.None(),
        };

        Ok(ModelInterface {
            model,
            data_type: sample_data.get_data_type(),
            task_type,
            schema,
            sample_data,
            model_type,
            model_interface_type: ModelInterfaceType::Base,
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

    /// Save the model to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[pyo3(signature = (path, **kwargs))]
    pub fn save_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None
        if self.model.is_none(py) {
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Model.to_string()).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method("dump", (&self.model, full_save_path), kwargs)?;

        Ok(save_path)
    }

    /// Load the model from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    #[pyo3(signature = (path, **kwargs))]
    pub fn load_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.model = joblib.call_method("load", (load_path,), kwargs)?.into();

        Ok(())
    }

    /// Create a feature schema
    ///
    /// # Arguments
    ///
    /// * `name` - Name of the feature
    ///
    /// # Returns
    ///
    /// * `PyResult<FeatureMap>` - FeatureMap
    pub fn create_feature_schema(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature

        let mut data = self.sample_data.get_data(py)?.bind(py).clone();

        // if data is instance of DataInterface, get the data
        if data.is_instance_of::<DataInterface>() {
            data = data.getattr("data")?;
        }

        let feature_map = generate_feature_schema(&data, &self.data_type)?;

        self.schema = feature_map.clone();

        Ok(feature_map)
    }

    /// Save the interface model
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to save the data
    /// * `kwargs` - Additional save kwargs
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, **kwargs))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // save data
        let model_uri = self.save_model(py, path.clone(), kwargs)?;

        // if sample_data is not None, save the sample data
        let sample_data_uri = self.sample_data.save_data(py, path).unwrap_or_else(|e| {
            warn!("Failed to save sample data. Defaulting to None: {}", e);
            None
        });

        self.schema = self.create_feature_schema(py)?;

        Ok(ModelInterfaceSaveMetadata {
            model_uri,
            preprocessor_uri: None,
            preprocessor_name: None,
            sample_data_uri,
            onnx_model_uri: None,
            extra_metadata: HashMap::new(),
        })
    }

    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    #[pyo3(signature = (**kwargs))]
    pub fn convert_to_onnx(
        &mut self,
        py: Python,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        OnnxModelConverter::convert_model(
            py,
            &self.model.bind(py),
            &self.sample_data,
            &self.model_interface_type,
            &self.model_type,
            kwargs,
        )?;

        Ok(())
    }
}
