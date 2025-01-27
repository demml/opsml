use crate::base::{parse_save_kwargs, LoadKwargs, SaveKwargs};
use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::model::onnx::OnnxModelConverter;
use crate::model::{SampleData, TaskType};
use crate::types::{Feature, FeatureSchema, ModelInterfaceType, ModelType};
use crate::OnnxSession;
use opsml_utils::FileUtils;
use opsml_utils::PyHelperFuncs;

use crate::model::base::utils;
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
use std::path::{Path, PathBuf};

use tracing::{debug, error, info, span, warn, Level};

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
    pub save_kwargs: Option<SaveKwargs>,
}

#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (model_uri, data_processor_map=HashMap::new(), sample_data_uri=None, onnx_model_uri=None,  drift_profile_uri=None, extra_metadata=HashMap::new(), save_kwargs=None))]
    pub fn new(
        model_uri: PathBuf,
        data_processor_map: Option<HashMap<String, DataProcessor>>,
        sample_data_uri: Option<PathBuf>,
        onnx_model_uri: Option<PathBuf>,
        drift_profile_uri: Option<PathBuf>,
        extra_metadata: HashMap<String, String>,
        save_kwargs: Option<SaveKwargs>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            model_uri,
            sample_data_uri,
            onnx_model_uri,
            data_processor_map: data_processor_map.unwrap_or_default(),
            drift_profile_uri,
            extra_metadata,
            save_kwargs,
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
    pub fn set_onnx_session(&mut self, onnx_session: Option<&OnnxSession>) {
        if let Some(onnx_session) = onnx_session {
            self.onnx_session = Some(onnx_session.clone());
        } else {
            self.onnx_session = None;
        }
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
    #[pyo3(signature = (path, to_onnx=false, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        let span = span!(Level::INFO, "Saving Model Interface").entered();
        let _ = span.enter();

        debug!("Saving model interface");

        // get onnx and model kwargs
        let (onnx_kwargs, model_kwargs, _) = parse_save_kwargs(py, &save_kwargs);

        // save model
        let model_uri = self.save_model(py, &path, model_kwargs.as_ref())?;

        // if to_onnx is true, convert the model to onnx
        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(self.save_onnx_model(py, &path, onnx_kwargs.as_ref())?);
        }

        let sample_data_uri = self.save_data(py, &path, None)?;

        let drift_profile_uri = if self.drift_profile.is_empty() {
            None
        } else {
            Some(self.save_drift_profile(&path)?)
        };

        self.schema = self.create_feature_schema(py)?;

        Ok(ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map: HashMap::new(),
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra_metadata: HashMap::new(),
            save_kwargs,
        })
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

    /// Dynamically load the model interface components
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to load from
    /// * `model` - Whether to load the model (default: true)
    /// * `onnx` - Whether to load the onnx model (default: false)
    /// * `drift_profile` - Whether to load the drift profile (default: false)
    /// * `sample_data` - Whether to load the sample data (default: false)
    /// * `load_kwargs` - Additional load kwargs to pass to the individual load methods
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, model=true, onnx=false, drift_profile=false, sample_data=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        &mut self,
        py: Python,
        path: PathBuf,
        model: bool,
        onnx: bool,
        drift_profile: bool,
        sample_data: bool,
        load_kwargs: Option<LoadKwargs>,
    ) -> PyResult<()> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        if model {
            self.load_model(py, &path, load_kwargs.model_kwargs(py))?;
        }

        if onnx {
            self.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
        }

        if drift_profile {
            self.load_drift_profile(&path)?;
        }

        if sample_data {
            self.load_data(py, &path, None)?;
        }

        Ok(())
    }
}

impl ModelInterface {
    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    pub fn convert_to_onnx(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Converting model to ONNX").entered();
        let _ = span.enter();

        if self.onnx_session.is_some() {
            info!("Model has already been converted to ONNX. Skipping conversion.");
            return Ok(());
        }

        self.onnx_session = Some(OnnxModelConverter::convert_model(
            py,
            self.model.bind(py),
            &self.sample_data,
            &self.model_interface_type,
            &self.model_type,
            path,
            kwargs,
        )?);

        info!("Model converted to ONNX");

        Ok(())
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
    pub fn save_drift_profile(&mut self, path: &Path) -> PyResult<PathBuf> {
        let span = span!(tracing::Level::INFO, "Save Drift Profile");
        let _enter = span.enter();

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
        info!("Drift profile saved");

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
    pub fn load_drift_profile(&mut self, path: &Path) -> PyResult<()> {
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

    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    pub fn save_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Saving ONNX Model").entered();
        let _ = span.enter();

        if self.onnx_session.is_none() {
            self.convert_to_onnx(py, path, kwargs)?;
        }

        let save_path = PathBuf::from(SaveName::OnnxModel.to_string()).with_extension(Suffix::Onnx);
        let full_save_path = path.join(&save_path);
        let bytes = self.onnx_session.as_ref().unwrap().model_bytes(py)?;
        fs::write(&full_save_path, bytes)?;

        info!("ONNX model saved");

        Ok(save_path)
    }

    /// Save the model to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    pub fn save_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Saving model").entered();
        let _ = span.enter();

        // check if data is None
        if self.model.is_none(py) {
            error!("No model detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method("dump", (&self.model, full_save_path), kwargs)?;

        info!("Model saved");

        Ok(save_path)
    }

    /// Saves the sample data
    pub fn save_data(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Option<PathBuf>> {
        // if sample_data is not None, save the sample data
        let sample_data_uri = self
            .sample_data
            .save_data(py, path, kwargs)
            .unwrap_or_else(|e| {
                warn!("Failed to save sample data. Defaulting to None: {}", e);
                None
            });

        Ok(sample_data_uri)
    }

    /// Load the sample data
    pub fn load_data(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        // load sample data
        self.sample_data = SampleData::load_data(py, path, &self.data_type, kwargs)?;

        Ok(())
    }

    /// Load the model from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Load ONNX Model");
        let _ = span.enter();

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

        info!("ONNX model loaded");

        Ok(())
    }

    /// Load the model from a file as well as sample data
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    pub fn load_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Loading Model").entered();
        let _ = span.enter();

        let load_path = path.join(SaveName::Model).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.model = joblib
            .call_method("load", (load_path,), kwargs)
            .map_err(|e| {
                error!("Failed to load model. Error: {}", e);
                OpsmlError::new_err(format!("Failed to load model. Error: {}", e))
            })?
            .into();

        info!("Model loaded");

        Ok(())
    }
}
