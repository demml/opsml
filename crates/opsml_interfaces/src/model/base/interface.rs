use crate::base::{parse_save_kwargs, ExtraMetadata, ModelLoadKwargs, ModelSaveKwargs};
use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::model::onnx::OnnxModelConverter;
use crate::model::SampleData;
use crate::types::{FeatureSchema, ProcessorType};
use crate::OnnxSession;
use opsml_utils::FileUtils;
use opsml_utils::PyHelperFuncs;
use scouter_client::{CustomDriftProfile, DriftType, PsiDriftProfile, SpcDriftProfile};

use crate::model::base::utils;
use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_types::{
    interfaces::{ModelInterfaceType, ModelType, TaskType},
    SaveName, Suffix,
};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use rand::Rng;
use scouter_client::{drifter::PyDrifter, DataType as DriftDataType};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use pyo3::gc::PyVisit;
use pyo3::PyTraverseError;
use serde_json::Value;
use tracing::{debug, error, info, instrument, warn};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataProcessor {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub uri: PathBuf,
    #[pyo3(get)]
    pub r#type: ProcessorType,
}

#[pymethods]
impl DataProcessor {
    #[new]
    pub fn new(name: String, uri: PathBuf, r#type: ProcessorType) -> Self {
        DataProcessor { name, uri, r#type }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelInterfaceSaveMetadata {
    #[pyo3(get)]
    pub model_uri: PathBuf,

    #[pyo3(get)]
    pub data_processor_map: HashMap<String, DataProcessor>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sample_data_uri: Option<PathBuf>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub onnx_model_uri: Option<PathBuf>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub drift_profile_uri: Option<PathBuf>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra: Option<ExtraMetadata>,

    #[pyo3(get)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub save_kwargs: Option<ModelSaveKwargs>,
}

#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (model_uri, data_processor_map=HashMap::new(), sample_data_uri=None, onnx_model_uri=None,  drift_profile_uri=None, extra=None, save_kwargs=None))]
    pub fn new(
        model_uri: PathBuf,
        data_processor_map: Option<HashMap<String, DataProcessor>>,
        sample_data_uri: Option<PathBuf>,
        onnx_model_uri: Option<PathBuf>,
        drift_profile_uri: Option<PathBuf>,
        extra: Option<ExtraMetadata>,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            model_uri,
            sample_data_uri,
            onnx_model_uri,
            data_processor_map: data_processor_map.unwrap_or_default(),
            drift_profile_uri,
            extra,
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
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelInterfaceMetadata {
    #[pyo3(get)]
    pub task_type: TaskType,

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub data_type: DataType,

    #[pyo3(get)]
    pub onnx_session: Option<OnnxSession>,

    #[pyo3(get)]
    pub schema: FeatureSchema,

    #[pyo3(get)]
    pub save_metadata: ModelInterfaceSaveMetadata,

    #[pyo3(get)]
    pub extra_metadata: HashMap<String, String>,

    #[pyo3(get)]
    pub interface_type: ModelInterfaceType,

    pub model_specific_metadata: Value,
}

#[pymethods]
impl ModelInterfaceMetadata {
    #[new]
    #[pyo3(signature = (save_metadata, task_type=TaskType::Other, model_type=ModelType::Unknown, data_type=DataType::NotProvided, schema=FeatureSchema::default(),interface_type=ModelInterfaceType::Base, onnx_session=None, extra_metadata=HashMap::new()))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        save_metadata: ModelInterfaceSaveMetadata,
        task_type: TaskType,
        model_type: ModelType,
        data_type: DataType,
        schema: FeatureSchema,
        interface_type: ModelInterfaceType,
        onnx_session: Option<OnnxSession>,
        extra_metadata: HashMap<String, String>,
    ) -> Self {
        ModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            onnx_session,
            schema,
            interface_type,
            save_metadata,
            extra_metadata,
            model_specific_metadata: Value::Null,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelInterfaceMetadata {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[pyclass(subclass)]
#[derive(Debug)]
pub struct ModelInterface {
    #[pyo3(get)]
    pub model: Option<PyObject>,

    #[pyo3(get, set)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub task_type: TaskType,

    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub interface_type: ModelInterfaceType,

    pub onnx_session: Option<Py<OnnxSession>>,

    #[pyo3(get)]
    pub drift_profile: Vec<PyObject>,

    pub sample_data: SampleData,
}

#[pymethods]
impl ModelInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=None, schema=None,drift_profile=None, **_kwargs))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
        schema: Option<FeatureSchema>,
        drift_profile: Option<&Bound<'py, PyAny>>,
        _kwargs: Option<&Bound<'_, PyDict>>,
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
            Some(model) => Some(model.into_py_any(py)?),
            None => None,
        };

        let profiles = match drift_profile {
            Some(profile) => utils::extract_drift_profile(profile)?,
            None => vec![],
        };

        Ok(ModelInterface {
            model,
            data_type: sample_data.get_data_type(),
            task_type: task_type.unwrap_or(TaskType::Other),
            schema,
            sample_data,
            model_type,
            interface_type: ModelInterfaceType::Base,
            onnx_session: None,
            drift_profile: profiles,
        })
    }

    #[getter]
    pub fn get_onnx_session(&self, py: Python) -> PyResult<Option<Py<OnnxSession>>> {
        // return mutable reference to onnx session
        Ok(self.onnx_session.as_ref().map(|sess| sess.clone_ref(py)))
    }

    #[setter]
    pub fn set_onnx_session(&mut self, onnx_session: Option<Py<OnnxSession>>) {
        self.onnx_session = onnx_session;
    }

    #[setter]
    pub fn set_model(&mut self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = model.py();

        // check if data is None
        if PyAnyMethods::is_none(model) {
            self.model = None;
            return Ok(());
        } else {
            self.model = Some(model.into_py_any(py)?);
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
    #[instrument(skip(self, py, path, to_onnx, save_kwargs) name = "save_model_interface")]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        debug!("Saving model interface");

        // get onnx and model kwargs
        let (onnx_kwargs, model_kwargs, _) = parse_save_kwargs(py, &save_kwargs);

        // save model
        let model_uri = self
            .save_model(py, &path, model_kwargs.as_ref())
            .map_err(|e| {
                error!("Failed to save model. Error: {}", e);
                e
            })?;

        // if to_onnx is true, convert the model to onnx
        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(
                self.save_onnx_model(py, &path, onnx_kwargs.as_ref())
                    .map_err(|e| {
                        error!("Failed to save ONNX model. Error: {}", e);
                        e
                    })?,
            );
        }

        let sample_data_uri = self.save_data(py, &path, None).map_err(|e| {
            error!("Failed to save sample data. Error: {}", e);
            e
        })?;

        let drift_profile_uri = if self.drift_profile.is_empty() {
            None
        } else {
            Some(self.save_drift_profile(py, &path).map_err(|e| {
                error!("Failed to save drift profile. Error: {}", e);
                e
            })?)
        };

        self.schema = self.create_feature_schema(py).map_err(|e| {
            error!("Failed to create feature schema. Error: {}", e);
            e
        })?;

        let save_metadata = ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map: HashMap::new(),
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra: None,
            save_kwargs,
        };

        // if onnx session is not None, get the session and extract it from py
        let onnx_session = self.onnx_session.as_ref().map(|sess| {
            let sess = sess.bind(py);
            // extract OnnxSession from py object
            sess.extract::<OnnxSession>().unwrap()
        });

        let metadata = ModelInterfaceMetadata::new(
            save_metadata,
            self.task_type.clone(),
            self.model_type.clone(),
            self.data_type.clone(),
            self.schema.clone(),
            self.interface_type.clone(),
            onnx_session,
            HashMap::new(),
        );

        Ok(metadata)
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

        let profile = drifter.create_drift_profile(py, data, config, data_type)?;
        self.drift_profile.push(profile.clone().into_py_any(py)?);

        Ok(profile)
    }

    /// Dynamically load the model interface components
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to load from
    /// * `onnx` - Whether to load the onnx model (default: false)
    /// * `load_kwargs` - Additional load kwargs to pass to the individual load methods
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceMetadata>` - DataInterfaceMetadata
    #[pyo3(signature = (path, onnx=false, load_kwargs=None, ))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        &mut self,
        py: Python,
        path: PathBuf,
        onnx: bool,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> PyResult<()> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        self.load_model(py, &path, load_kwargs.model_kwargs(py))?;
        self.load_drift_profile(py, &path)?;
        self.load_data(py, &path, None)?;

        if onnx {
            self.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
        }

        Ok(())
    }

    #[staticmethod]
    pub fn from_metadata(
        py: Python,
        metadata: &ModelInterfaceMetadata,
    ) -> PyResult<ModelInterface> {
        let interface = ModelInterface {
            model: None,
            data_type: metadata.data_type.clone(),
            task_type: metadata.task_type.clone(),
            schema: metadata.schema.clone(),
            model_type: metadata.model_type.clone(),
            interface_type: metadata.interface_type.clone(),
            onnx_session: metadata
                .onnx_session
                .as_ref()
                .map(|session| Py::new(py, session.clone()).unwrap()),
            drift_profile: vec![],
            sample_data: SampleData::default(),
        };

        Ok(interface)
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref model) = self.model {
            visit.call(model)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.model = None;
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
    #[instrument(skip_all)]
    pub fn convert_to_onnx(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        if self.onnx_session.is_some() {
            info!("Model has already been converted to ONNX. Skipping conversion.");
            return Ok(());
        }

        let session = OnnxModelConverter::convert_model(
            py,
            self.model.as_ref().unwrap().bind(py),
            &self.sample_data,
            &self.interface_type,
            &self.model_type,
            path,
            kwargs,
        )?;

        self.onnx_session = Some(Py::new(py, session)?);

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
    #[instrument(skip_all, name = "save_drift_profile")]
    pub fn save_drift_profile(&mut self, py: Python, path: &Path) -> PyResult<PathBuf> {
        let save_dir = PathBuf::from(SaveName::Drift);
        if !save_dir.exists() {
            fs::create_dir_all(&save_dir).unwrap();
        }

        let save_path = path.join(save_dir.clone());
        for profile in self.drift_profile.iter() {
            let drift_type = profile
                .bind(py)
                .getattr("config")?
                .getattr("drift_type")?
                .extract::<String>()?;

            // add small hex to filename to avoid overwriting
            // this would only have if someone creates multiple drift profiles of the same type
            // probably won't happen, but lets be a little safe
            let random_hex: String = rand::rng()
                .sample_iter(&rand::distr::Alphanumeric)
                .take(3)
                .map(char::from)
                .collect();

            let filename = format!("{}-{}-{}", drift_type, SaveName::DriftProfile, random_hex);
            let profile_save_path = save_path.join(filename).with_extension(Suffix::Json);

            profile.call_method1(py, "save_to_json", (Some(profile_save_path),))?;
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
    pub fn load_drift_profile(&mut self, py: Python, path: &Path) -> PyResult<()> {
        let load_dir = path.join(SaveName::Drift);

        if !load_dir.exists() {
            return Ok(());
        }

        // list all files in dir
        let files = FileUtils::list_files(load_dir)?;

        for filepath in files {
            // get file name
            let filename = filepath.file_name().unwrap().to_str().unwrap();
            let drift_type = DriftType::from_value(&filename.split('-').next().unwrap());

            // fail if drift type is not found
            if drift_type.is_none() {
                return Err(OpsmlError::new_err(format!(
                    "Drift type not found in drift profile filename: {}",
                    filename
                )));
            }

            // load file to json string
            let file = std::fs::read_to_string(&path).map_err(|_| {
                OpsmlError::new_err(format!("Failed to read drift profile file: {}", filename))
            })?;

            match drift_type.unwrap() {
                DriftType::Spc => {
                    let profile = SpcDriftProfile::model_validate_json(file);
                    self.drift_profile.push(profile.into_py_any(py)?);
                }
                DriftType::Psi => {
                    let profile = PsiDriftProfile::model_validate_json(file);
                    self.drift_profile.push(profile.into_py_any(py)?);
                }
                DriftType::Custom => {
                    let profile = CustomDriftProfile::model_validate_json(file);
                    self.drift_profile.push(profile.into_py_any(py)?);
                }
            }
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
    #[instrument(skip_all)]
    pub fn save_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        if self.onnx_session.is_none() {
            self.convert_to_onnx(py, path, kwargs)?;
        }

        let save_path = PathBuf::from(SaveName::OnnxModel.to_string()).with_extension(Suffix::Onnx);
        let full_save_path = path.join(&save_path);

        let bytes: Vec<u8> = self
            .onnx_session
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method0("model_bytes")?
            .extract()?;

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
    #[instrument(skip_all)]
    pub fn save_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None
        if self.model.is_none() {
            error!("No model detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method(
            "dump",
            (self.model.as_ref().unwrap().bind(py), full_save_path),
            kwargs,
        )?;

        info!("Model saved");

        Ok(save_path)
    }

    /// Saves the sample data
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `path` - Path to save the data
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[instrument(skip_all)]
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
    #[instrument(skip_all)]
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
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

        let sess = OnnxSession::load_onnx_session(py, load_path, kwargs)?;

        self.onnx_session
            .as_ref()
            .unwrap()
            .setattr(py, "session", Some(sess))?;

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
    #[instrument(skip_all)]
    pub fn load_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Model).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.model = Some(
            joblib
                .call_method("load", (load_path,), kwargs)
                .map_err(|e| {
                    error!("Failed to load model. Error: {}", e);
                    OpsmlError::new_err(format!("Failed to load model. Error: {e}"))
                })?
                .unbind(),
        );

        info!("Model loaded");

        Ok(())
    }
}
