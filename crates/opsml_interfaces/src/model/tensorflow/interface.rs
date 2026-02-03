use crate::base::{parse_save_kwargs, ModelInterfaceSaveMetadata};
use crate::data::generate_feature_schema;
use crate::data::DataInterface;
use crate::error::{ModelInterfaceError, OnnxError};
use crate::model::tensorflow::TensorFlowSampleData;
use crate::model::ModelInterface;
use crate::types::{FeatureSchema, ProcessorType};
use crate::ModelInterfaceMetadata;
use crate::OnnxConverter;
use crate::OnnxSession;
use crate::{DataProcessor, ModelLoadKwargs, ModelSaveKwargs};
use opsml_types::{CommonKwargs, SaveName, Suffix};
use opsml_types::{DataType, ModelInterfaceType, ModelType, TaskType};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument, warn};

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct TensorFlowModel {
    #[pyo3(get)]
    pub model: Option<Py<PyAny>>,

    #[pyo3(get)]
    pub preprocessor: Option<Py<PyAny>>,

    #[pyo3(get, set)]
    preprocessor_name: String,

    pub onnx_session: Option<Py<OnnxSession>>,

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub interface_type: ModelInterfaceType,

    pub sample_data: TensorFlowSampleData,
}

#[pymethods]
impl TensorFlowModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, preprocessor=None, sample_data=None, task_type=None,  drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        preprocessor: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> Result<(Self, ModelInterface), ModelInterfaceError> {
        let tf = py.import("tensorflow")?;
        // check if model is base estimator for sklearn validation
        let model = if let Some(model) = model {
            let tf_model = tf.getattr("keras")?.getattr("Model")?;
            if model.is_instance(&tf_model).unwrap() {
                Some(model.into_py_any(py)?)
            } else {
                return Err(ModelInterfaceError::TensorFlowTypeError);
            }
        } else {
            None
        };

        let version = tf.getattr("__version__")?.extract::<String>().ok();

        let mut model_interface =
            ModelInterface::new(py, None, None, task_type, drift_profile, version)?;

        // override ModelInterface SampleData with TensorFlowSampleData
        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => TensorFlowSampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {e}");
                TensorFlowSampleData::default()
            }),
            None => TensorFlowSampleData::default(),
        };

        model_interface.data_type = sample_data.get_data_type();

        let mut preprocessor_name = CommonKwargs::Undefined.to_string();

        let preprocessor = match preprocessor {
            Some(preprocessor) => {
                preprocessor_name = preprocessor
                    .getattr("__class__")?
                    .getattr("__name__")?
                    .to_string();
                Some(preprocessor.into_py_any(py)?)
            }
            None => None,
        };
        Ok((
            TensorFlowModel {
                model,
                preprocessor,
                preprocessor_name,
                sample_data,
                interface_type: ModelInterfaceType::TensorFlow,
                model_type: ModelType::TensorFlow,
                onnx_session: None,
            },
            // pass all the arguments to the ModelInterface
            model_interface,
        ))
    }

    #[setter]
    pub fn set_model(&mut self, model: &Bound<'_, PyAny>) -> Result<(), ModelInterfaceError> {
        let py = model.py();

        // check if data is None
        if PyAnyMethods::is_none(model) {
            self.model = None;
            return Ok(());
        } else {
            let tf_model = py
                .import("tensorflow")?
                .getattr("keras")?
                .getattr("Model")?;
            if model.is_instance(&tf_model).unwrap() {
                self.model = Some(model.into_py_any(py)?)
            } else {
                return Err(ModelInterfaceError::TensorFlowTypeError);
            }
        };

        Ok(())
    }

    #[getter]
    pub fn get_onnx_session<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Option<&Bound<'py, OnnxSession>>, ModelInterfaceError> {
        // return mutable reference to onnx session
        Ok(self.onnx_session.as_ref().map(|sess| sess.bind(py)))
    }

    #[setter]
    pub fn set_onnx_session(&mut self, onnx_session: Option<Bound<'_, OnnxSession>>) {
        self.onnx_session = onnx_session.map(|sess| sess.unbind()).or_else(|| {
            warn!("Failed to set onnx session. Defaulting to None");
            None
        });
    }

    #[setter]
    pub fn set_sample_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        sample_data: &Bound<'py, PyAny>,
    ) -> Result<(), ModelInterfaceError> {
        self_.sample_data = TensorFlowSampleData::new(sample_data)?;

        // set the data type
        self_.as_super().data_type = self_.sample_data.get_data_type();

        Ok(())
    }

    #[getter]
    pub fn get_sample_data<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, PyAny>, ModelInterfaceError> {
        Ok(self.sample_data.get_data(py).unwrap().bind(py).clone())
    }

    #[getter]
    pub fn get_preprocessor<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.clone_ref(py).into_bound_py_any(py).unwrap())
    }
    #[setter]
    #[allow(clippy::needless_lifetimes)]
    pub fn set_preprocessor<'py>(
        &mut self,
        py: Python,
        preprocessor: &Bound<'py, PyAny>,
    ) -> Result<(), ModelInterfaceError> {
        if PyAnyMethods::is_none(preprocessor) {
            self.preprocessor = None;
            self.preprocessor_name = CommonKwargs::Undefined.to_string();
            Ok(())
        } else {
            let preprocessor_name = preprocessor
                .getattr("__class__")?
                .getattr("__name__")?
                .to_string();
            self.preprocessor = Some(preprocessor.into_py_any(py)?);
            self.preprocessor_name = preprocessor_name;
            Ok(())
        }
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
    #[pyo3(signature = (path, save_kwargs=None))]
    #[instrument(skip_all, name = "save_tensorflow_interface")]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Result<ModelInterfaceMetadata, ModelInterfaceError> {
        debug!("Saving drift profile");
        let drift_profile_uri_map = if self_.as_super().drift_profile.is_empty() {
            None
        } else {
            Some(self_.as_super().save_drift_profile(py, &path)?)
        };

        // parse the save args
        let kwargs = parse_save_kwargs(py, save_kwargs.as_ref());

        debug!("Saving preprocessor");
        let preprocessor_entity = if self_.preprocessor.is_none() {
            None
        } else {
            let uri = self_.save_preprocessor(py, &path, kwargs.preprocessor.as_ref())?;
            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri,
                r#type: ProcessorType::Preprocessor,
            })
        };

        debug!("Saving sample data");
        let sample_data_uri = self_.save_data(py, &path, None)?;

        debug!("Creating feature schema");
        self_.as_super().schema = self_.create_feature_schema(py)?;

        let mut onnx_model_uri = None;

        if kwargs.save_onnx {
            debug!("Saving ONNX model");
            onnx_model_uri = Some(self_.save_onnx_model(py, &path, kwargs.onnx.as_ref())?);
        }

        debug!("Saving model");
        let model_uri = self_.save_model(py, &path, kwargs.model.as_ref())?;

        let data_processor_map = preprocessor_entity
            .map(|preprocessor| {
                let mut map = HashMap::new();
                map.insert(preprocessor.name.clone(), preprocessor);
                map
            })
            .unwrap_or_default();

        let save_metadata = ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map,
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri_map,
            extra: None,
            save_kwargs,
        };

        let onnx_session = {
            self_.onnx_session.as_ref().map(|sess| {
                let sess = sess.bind(py);
                // extract OnnxSession from py object
                sess.extract::<OnnxSession>().unwrap()
            })
        };

        let metadata = ModelInterfaceMetadata::new(
            save_metadata,
            self_.as_super().task_type.clone(),
            self_.model_type.clone(),
            self_.sample_data.get_data_type(),
            self_.as_super().schema.clone(),
            self_.interface_type.clone(),
            onnx_session,
            HashMap::new(),
            self_.as_super().version.clone(),
        );

        Ok(metadata)
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
    #[pyo3(signature = (path, metadata, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    #[instrument(skip_all)]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> Result<(), ModelInterfaceError> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        debug!("Loading model");
        let model_path = path.join(&metadata.model_uri);
        self_.load_model(py, &model_path, load_kwargs.model_kwargs(py))?;

        if load_kwargs.load_onnx {
            debug!("Loading ONNX model");
            let onnx_path = path.join(
                &metadata
                    .onnx_model_uri
                    .ok_or_else(|| ModelInterfaceError::MissingOnnxUriError)?,
            );
            self_.load_onnx_model(py, &onnx_path, load_kwargs.onnx_kwargs(py))?;
        }

        let data_type = self_.as_super().data_type.clone();
        if metadata.sample_data_uri.is_some() {
            debug!("Loading sample data");
            let sample_data_path = path.join(
                &metadata
                    .sample_data_uri
                    .ok_or_else(|| ModelInterfaceError::MissingSampleDataUriError)?,
            );
            self_.load_data(py, &sample_data_path, &data_type, None)?;
        }

        if !metadata.data_processor_map.is_empty() {
            // get first key from metadata.save_metadata.data_processor_map.keys() or default to unknow
            let processor = metadata
                .data_processor_map
                .values()
                .next()
                .ok_or_else(|| ModelInterfaceError::MissingPreprocessorUriError)?;

            let preprocessor_uri = path.join(&processor.uri);

            self_.load_preprocessor(py, &preprocessor_uri, load_kwargs.preprocessor_kwargs(py))?;
        }

        debug!("Loading drift profile");
        if let Some(ref drift_map) = metadata.drift_profile_uri_map {
            self_.as_super().load_drift_profile(py, &path, drift_map)?;
        }

        Ok(())
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref preprocessor) = self.preprocessor {
            visit.call(preprocessor)?;
        }

        if let Some(ref model) = self.model {
            visit.call(model)?;
        }

        if let Some(ref onnx_session) = self.onnx_session {
            visit.call(onnx_session)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.preprocessor = None;
        self.model = None;
        self.onnx_session = None;
    }
}

impl TensorFlowModel {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &ModelInterfaceMetadata,
    ) -> Result<Bound<'py, PyAny>, ModelInterfaceError> {
        // get first key from metadata.save_metadata.data_processor_map.keys() or default to unknow
        let preprocessor_name = metadata
            .save_metadata
            .data_processor_map
            .iter()
            .filter(|(_, v)| v.r#type == ProcessorType::Preprocessor)
            .map(|(k, _)| k)
            .next()
            .unwrap_or(&CommonKwargs::Undefined.to_string())
            .to_string();

        // convert onnx session to to Py<OnnxSession>
        let onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        let model_interface = TensorFlowModel {
            preprocessor: None,
            preprocessor_name,
            onnx_session,
            model: None,
            model_type: metadata.model_type.clone(),
            interface_type: metadata.interface_type.clone(),
            sample_data: TensorFlowSampleData::default(),
        };

        let mut interface = ModelInterface::new(
            py,
            None,
            None,
            Some(metadata.task_type.clone()),
            None,
            Some(metadata.version.clone()),
        )?;

        interface.schema = metadata.schema.clone();
        interface.data_type = metadata.data_type.clone();

        let interface = Py::new(py, (model_interface, interface))?.into_bound_py_any(py)?;

        Ok(interface)
    }

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
    ) -> Result<(), ModelInterfaceError> {
        let session = OnnxConverter::convert_model(
            py,
            self.model.as_ref().unwrap().bind(py),
            &self.sample_data,
            &self.interface_type,
            &self.model_type,
            path,
            kwargs,
        )?;

        self.onnx_session = Some(Py::new(py, session)?);

        Ok(())
    }

    /// Save the preprocessor to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[instrument(skip_all)]
    pub fn save_preprocessor(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, ModelInterfaceError> {
        if self.preprocessor.is_none() {
            error!("No preprocessor detected in interface for saving");
            return Err(ModelInterfaceError::NoPreprocessorError);
        }
        let save_path = PathBuf::from(SaveName::Preprocessor).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;
        // Save the data using joblib
        joblib.call_method("dump", (&self.preprocessor, full_save_path), kwargs)?;

        debug!("Preprocessor saved");
        Ok(save_path)
    }
    /// Load the preprocessor from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    #[instrument(skip_all)]
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let joblib = py.import("joblib")?;
        // Load the data using joblib
        let preprocessor = joblib.call_method("load", (path,), kwargs)?;

        self.preprocessor = Some(preprocessor.unbind());

        debug!("Preprocessor loaded");
        Ok(())
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
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, ModelInterfaceError> {
        // check if model is None
        if self.model.is_none() {
            return Err(ModelInterfaceError::NoModelError);
        }

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Keras);
        let full_save_path = path.join(&save_path);

        // Save torch model
        self.model
            .as_ref()
            .unwrap()
            .bind(py)
            .call_method("save", (full_save_path,), kwargs)?;

        debug!("Model saved");

        Ok(save_path)
    }

    #[instrument(skip_all)]
    pub fn load_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), ModelInterfaceError> {
        let tf_models = py
            .import("tensorflow")?
            .getattr("keras")?
            .getattr("models")?;

        let model = tf_models.call_method("load_model", (path,), kwargs)?;

        self.model = Some(model.clone().unbind());

        Ok(())
    }

    /// Saves the sample data
    pub fn save_data(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Option<PathBuf>, ModelInterfaceError> {
        // if sample_data is not None, save the sample data
        let sample_data_uri = self
            .sample_data
            .save_data(py, path, kwargs)
            .unwrap_or_else(|e| {
                warn!("Failed to save sample data. Defaulting to None: {e}");
                None
            });

        Ok(sample_data_uri)
    }

    /// Load the sample data
    #[instrument(skip_all)]
    pub fn load_data(
        &mut self,
        py: Python,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), ModelInterfaceError> {
        // load sample data

        self.sample_data = TensorFlowSampleData::load_data(py, path, data_type, kwargs)?;

        debug!("Sample data loaded");

        Ok(())
    }

    /// Saves a model to onnx format
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    #[instrument(skip_all)]
    fn save_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, ModelInterfaceError> {
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

        debug!("ONNX model saved");

        Ok(save_path)
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
    ) -> Result<(), OnnxError> {
        if self.onnx_session.is_none() {
            return Err(OnnxError::SessionNotFound);
        }

        self.onnx_session.as_ref().unwrap().bind(py).call_method(
            "load_onnx_model",
            (path,),
            kwargs,
        )?;

        debug!("ONNX model loaded");

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

        Ok(generate_feature_schema(
            &data,
            &self.sample_data.get_data_type(),
        )?)
    }
}
