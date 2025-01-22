use crate::base::SaveArgs;
use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::model::onnx::OnnxModelConverter;
use crate::model::{SampleData, TaskType};
use crate::types::{Feature, FeatureSchema, ModelInterfaceType, ModelType};
use crate::OnnxSession;
use opsml_utils::FileUtils;
use opsml_utils::PyHelperFuncs;

use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_types::{SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use rand::Rng;
use scouter_client::{drifter::PyDrifter, DataType as DriftDataType, DriftProfile};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use tracing::debug;
use tracing::warn;

use super::utils;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataProcessor {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub uri: PathBuf,
}

#[pymethods]
impl DataProcessor {
    #[new]
    pub fn new(name: String, uri: PathBuf) -> Self {
        DataProcessor { name, uri }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ModelInterfaceSaveMetadata {
    #[pyo3(get)]
    pub model_uri: PathBuf,

    #[pyo3(get)]
    pub data_processor_map: HashMap<String, DataProcessor>,

    #[pyo3(get)]
    pub sample_data_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub onnx_model_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub drift_profile_uri: Option<PathBuf>,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,

    #[pyo3(get)]
    pub save_args: Option<SaveArgs>,
}

#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (model_uri, data_processor_map=HashMap::new(), sample_data_uri=None, onnx_model_uri=None,  drift_profile_uri=None, extra_metadata=HashMap::new(), save_args=None))]
    pub fn new(
        model_uri: PathBuf,
        data_processor_map: Option<HashMap<String, DataProcessor>>,
        sample_data_uri: Option<PathBuf>,
        onnx_model_uri: Option<PathBuf>,
        drift_profile_uri: Option<PathBuf>,
        extra_metadata: HashMap<String, String>,
        save_args: Option<SaveArgs>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            model_uri,
            sample_data_uri,
            onnx_model_uri,
            data_processor_map: data_processor_map.unwrap_or_default(),
            drift_profile_uri,
            extra_metadata,
            save_args,
        }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__json__(self)
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

    #[pyo3(get)]
    pub onnx_session: Option<OnnxSession>,

    #[pyo3(get)]
    pub drift_profile: Vec<DriftProfile>,

    pub sample_data: SampleData,
}

#[pymethods]
impl ModelInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=TaskType::Other, schema=None,drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: TaskType,
        schema: Option<FeatureSchema>,
        drift_profile: Option<&Bound<'py, PyAny>>,
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

        let profiles = match drift_profile {
            Some(profile) => utils::extract_drift_profile(profile)?,
            None => vec![],
        };

        Ok(ModelInterface {
            model,
            data_type: sample_data.get_data_type(),
            task_type,
            schema,
            sample_data,
            model_type,
            model_interface_type: ModelInterfaceType::Base,
            onnx_session: None,
            drift_profile: profiles,
        })
    }

    #[setter]
    pub fn set_model(&mut self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = model.py();

        // check if data is None
        if PyAnyMethods::is_none(model) {
            self.model = py.None();
            return Ok(());
        } else {
            self.model = model.into_py_any(py)?;
        };

        Ok(())
    }

    #[setter]
    pub fn set_drift_profile(&mut self, drift_profile: &Bound<'_, PyAny>) -> PyResult<()> {
        self.drift_profile = utils::extract_drift_profile(drift_profile)?;
        Ok(())
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

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Joblib);
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
        let load_path = path.join(SaveName::Model).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.model = joblib.call_method("load", (load_path,), kwargs)?.into();

        Ok(())
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
    #[pyo3(signature = (path, to_onnx=false, save_args=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_args: Option<SaveArgs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // get onnx and model kwargs
        let onnx_kwargs = save_args
            .as_ref()
            .and_then(|args| args.onnx_kwargs(py))
            .cloned();

        let model_kwargs = save_args
            .as_ref()
            .and_then(|args| args.model_kwargs(py))
            .cloned();

        debug!(
            "Saving model to: {:?} with save_args: {:?}",
            path, save_args
        );

        // save model
        let model_uri = self.save_model(py, path.clone(), model_kwargs.as_ref())?;

        // if sample_data is not None, save the sample data
        let sample_data_uri = self
            .sample_data
            .save_data(py, path.clone())
            .unwrap_or_else(|e| {
                warn!("Failed to save sample data. Defaulting to None: {}", e);
                None
            });

        // if to_onnx is true, convert the model to onnx
        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(self.save_onnx_model(py, path.clone(), onnx_kwargs.as_ref())?);
        }

        let drift_profile_uri = if self.drift_profile.is_empty() {
            None
        } else {
            Some(self.save_drift_profile(path.clone())?)
        };

        self.schema = self.create_feature_schema(py)?;

        Ok(ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map: HashMap::new(),
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra_metadata: HashMap::new(),
            save_args,
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
        if self.onnx_session.is_some() {
            warn!("Model has already been converted to ONNX. Skipping conversion.");
            return Ok(());
        }

        self.onnx_session = Some(OnnxModelConverter::convert_model(
            py,
            self.model.bind(py),
            &self.sample_data,
            &self.model_interface_type,
            &self.model_type,
            kwargs,
        )?);

        Ok(())
    }

    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    #[pyo3(signature = (path, **kwargs))]
    pub fn save_onnx_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        if self.onnx_session.is_none() {
            self.convert_to_onnx(py, kwargs)?;
        }

        let save_path = PathBuf::from(SaveName::OnnxModel.to_string()).with_extension(Suffix::Onnx);
        let full_save_path = path.join(&save_path);
        let bytes = self.onnx_session.as_ref().unwrap().model_bytes(py)?;
        fs::write(&full_save_path, bytes)?;

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
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        if self.onnx_session.is_none() {
            return Err(OpsmlError::new_err(
                "No ONNX model detected in interface for loading",
            ));
        }

        let load_path = path
            .join(SaveName::OnnxModel.to_string())
            .with_extension(Suffix::Onnx);

        self.onnx_session
            .as_mut()
            .unwrap()
            .load_onnx_model(py, load_path, kwargs)?;

        Ok(())
    }

    /// Create drift profile
    ///
    /// # Arguments
    ///
    /// * `data` - Data to create drift profile from
    /// * `config` - Configuration for drift profile
    /// * `data_type` - Data type for drift profile
    ///
    #[pyo3(signature = (data, config=None, data_type=None))]
    pub fn create_drift_profile<'py>(
        &mut self,
        py: Python<'py>,
        data: &Bound<'py, PyAny>,
        config: Option<&Bound<'py, PyAny>>,
        data_type: Option<&DataType>,
    ) -> PyResult<Bound<'py, PyAny>> {
        debug!("Creating drift profile");
        let drifter = PyDrifter::new();

        let data_type = data_type.and_then(|dt| match dt {
            DataType::Pandas => Some(&DriftDataType::Pandas),
            DataType::Numpy => Some(&DriftDataType::Numpy),
            DataType::Polars => Some(&DriftDataType::Polars),
            DataType::Arrow => Some(&DriftDataType::Arrow),
            _ => None,
        });

        let profile = drifter.internal_create_drift_profile(py, data, config, data_type)?;
        let py_profile = profile.profile(py)?;
        self.drift_profile.push(profile);

        Ok(py_profile)
    }

    /// Save drift profile
    ///
    /// # Arguments
    ///
    /// * `path` - Path to save drift profile
    ///
    /// # Returns
    ///
    /// * `PyResult<PathBuf>` - Path to saved drift profile
    pub fn save_drift_profile(&mut self, path: PathBuf) -> PyResult<PathBuf> {
        let save_dir = PathBuf::from(SaveName::Drift);
        if !save_dir.exists() {
            fs::create_dir_all(&save_dir).unwrap();
        }

        let save_path = path.join(save_dir.clone());
        for profile in self.drift_profile.iter() {
            let drift_type = profile.drift_type();

            // add small hex to filename to avoid overwriting
            // this would only have if someone creates multiple drift profiles of the same type
            // probably won't happen, but lets be a little safe
            let random_hex: String = rand::thread_rng()
                .sample_iter(&rand::distributions::Alphanumeric)
                .take(3)
                .map(char::from)
                .collect();

            let filename = format!(
                "{}_{}_{}",
                drift_type.to_string(),
                SaveName::DriftProfile,
                random_hex
            );
            let profile_save_path = save_path.join(filename).with_extension(Suffix::Json);

            profile.save_to_json(Some(profile_save_path))?
        }

        Ok(save_dir)
    }

    /// Load drift profile
    ///     
    /// # Arguments
    ///
    /// * `path` - Path to load drift profile
    ///
    /// # Returns
    ///
    /// * `PyResult<()>` - Result of loading drift profile
    pub fn load_drift_profile(&mut self, path: PathBuf) -> PyResult<()> {
        let load_dir = path.join(SaveName::Drift);

        if !load_dir.exists() {
            return Ok(());
        }

        // list all files in dir
        let files = FileUtils::list_files(load_dir)?;

        for filepath in files {
            let drift_profile = DriftProfile::load_from_json(filepath).map_err(|e| {
                OpsmlError::new_err(format!("Failed to load drift profile. Error: {}", e))
            })?;
            self.drift_profile.push(drift_profile);
        }

        Ok(())
    }
}
