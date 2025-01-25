use crate::base::{parse_save_kwargs, ModelInterfaceSaveMetadata};
use crate::model::torch::TorchSampleData;
use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use crate::ModelType;
use crate::{DataProcessor, LoadKwargs, SaveKwargs};
use crate::{OnnxModelConverter, OnnxSession};
use opsml_error::OpsmlError;
use opsml_types::DataType;
use opsml_types::{CommonKwargs, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use tracing::{debug, error, info, span, warn, Level};
#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct TorchModel {
    #[pyo3(get)]
    pub model: PyObject,

    #[pyo3(get)]
    pub preprocessor: PyObject,

    #[pyo3(get, set)]
    preprocessor_name: String,

    #[pyo3(get)]
    pub model_type: ModelType,

    #[pyo3(get)]
    pub model_interface_type: ModelInterfaceType,

    pub sample_data: TorchSampleData,
}

#[pymethods]
impl TorchModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, preprocessor=None, sample_data=None, task_type=TaskType::Other, schema=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        preprocessor: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: TaskType,
        schema: Option<FeatureSchema>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<(Self, ModelInterface)> {
        // check if model is base estimator for sklearn validation
        let model = if let Some(model) = model {
            let torch_module = py.import("torch")?.getattr("nn")?.getattr("Module")?;
            if model.is_instance(&torch_module).unwrap() {
                model.into_py_any(py)?
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an instance of torch.nn.Module",
                ));
            }
        } else {
            py.None()
        };

        let mut model_interface =
            ModelInterface::new(py, None, None, task_type, schema, drift_profile)?;

        // override ModelInterface SampleData with TorchSampleData
        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => TorchSampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {}", e);
                TorchSampleData::default()
            }),
            None => TorchSampleData::default(),
        };

        model_interface.data_type = sample_data.get_data_type();

        let mut preprocessor_name = CommonKwargs::Undefined.to_string();

        let preprocessor = match preprocessor {
            Some(preprocessor) => {
                preprocessor_name = preprocessor
                    .getattr("__class__")?
                    .getattr("__name__")?
                    .to_string();
                preprocessor.into_py_any(py)?
            }
            None => py.None(),
        };
        Ok((
            TorchModel {
                preprocessor,
                preprocessor_name,
                sample_data,
                model,
                model_interface_type: ModelInterfaceType::Torch,
                model_type: ModelType::Pytorch,
                onnx_session: None,
            },
            // pass all the arguments to the ModelInterface
            model_interface,
        ))
    }

    #[setter]
    pub fn set_model(&mut self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = model.py();

        // check if data is None
        if PyAnyMethods::is_none(model) {
            self.model = py.None();
            return Ok(());
        } else {
            let torch_module = py.import("torch")?.getattr("nn")?.getattr("Module")?;
            if model.is_instance(&torch_module).unwrap() {
                model.into_py_any(py)?
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an instance of torch.nn.Module",
                ));
            }
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
    pub fn set_sample_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        sample_data: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        self_.sample_data = TorchSampleData::new(sample_data)?;

        // set the data type
        self_.as_super().data_type = self_.sample_data.get_data_type();

        Ok(())
    }

    #[getter]
    pub fn get_sample_data(&self, py: Python<'_>) -> PyResult<PyObject> {
        self.sample_data.get_data(py)
    }

    #[getter]
    pub fn get_preprocessor<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        if self.preprocessor.is_none(py) {
            None
        } else {
            Some(
                self.preprocessor
                    .clone_ref(py)
                    .into_bound_py_any(py)
                    .unwrap(),
            )
        }
    }
    #[setter]
    #[allow(clippy::needless_lifetimes)]
    pub fn set_preprocessor<'py>(
        &mut self,
        py: Python,
        preprocessor: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        if PyAnyMethods::is_none(preprocessor) {
            self.preprocessor = py.None();
            self.preprocessor_name = CommonKwargs::Undefined.to_string();
            Ok(())
        } else {
            let preprocessor_name = preprocessor
                .getattr("__class__")?
                .getattr("__name__")?
                .to_string();
            self.preprocessor = preprocessor.into_py_any(py)?;
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
    #[pyo3(signature = (path, to_onnx=false, save_kwargs=None))]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // color text
        let span = span!(Level::INFO, "Saving TorchModel interface").entered();
        let _ = span.enter();

        // parse the save args
        let (onnx_kwargs, model_kwargs, preprocessor_kwargs) = parse_save_kwargs(py, &save_kwargs);

        debug!("Saving preprocessor");
        let preprocessor_entity = if self_.preprocessor.is_none(py) {
            None
        } else {
            let uri = self_.save_preprocessor(py, &path, preprocessor_kwargs.as_ref())?;
            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri,
            })
        };

        debug!("Saving sample data");
        let sample_data_uri = self_.save_data(py, &path, None)?;

        debug!("Saving model");
        let model_uri = self_.save_model(py, &path, model_kwargs.as_ref())?;

        let mut onnx_model_uri = None;
        let mut drift_profile_uri = None;
        // scope for parent
        {
            let parent = self_.as_super();

            debug!("Saving drift profile");
            if parent.drift_profile.is_empty() {
                drift_profile_uri = Some(parent.save_drift_profile(&path)?);
            };

            debug!("Creating feature schema");
            parent.schema = parent.create_feature_schema(py)?;

            if to_onnx {
                debug!("Saving ONNX model");
                onnx_model_uri = Some(parent.save_onnx_model(py, &path, onnx_kwargs.as_ref())?);
            }
        }

        let data_processor_map = preprocessor_entity
            .map(|preprocessor| {
                let mut map = HashMap::new();
                map.insert(preprocessor.name.clone(), preprocessor);
                map
            })
            .unwrap_or_default();

        let metadata = ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map,
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra_metadata: HashMap::new(),
            save_kwargs,
        };

        Ok(metadata)
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
    /// * `preprocessor` - Whether to load the preprocessor (default: false)
    /// * `load_kwargs` - Additional load kwargs to pass to the individual load methods
    ///
    /// # Returns
    ///
    /// * `PyResult<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, model=true, onnx=false, drift_profile=false, sample_data=false, preprocessor=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        model: bool,
        onnx: bool,
        drift_profile: bool,
        sample_data: bool,
        preprocessor: bool,
        load_kwargs: Option<LoadKwargs>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Loading TorchModel components").entered();
        let _ = span.enter();

        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        if model {
            debug!("Loading model");
            self_.load_model(py, &path, load_kwargs.model_kwargs(py))?;
        }

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();

            if onnx {
                parent.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
            }

            if drift_profile {
                parent.load_drift_profile(&path)?;
            }
        }

        if sample_data {
            let data_type = self_.as_super().data_type.clone();
            self_.load_data(py, &path, &data_type, None)?;
        }

        if preprocessor {
            self_.load_preprocessor(py, &path, load_kwargs.preprocessor_kwargs(py))?;
        }

        Ok(())
    }
}

impl TorchModel {
    /// Save the preprocessor to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    pub fn save_preprocessor(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Save Preprocessor").entered();
        let _ = span.enter();

        if self.preprocessor.is_none(py) {
            error!("No preprocessor detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }
        let save_path = PathBuf::from(SaveName::Preprocessor).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;
        // Save the data using joblib
        joblib
            .call_method("dump", (&self.preprocessor, full_save_path), kwargs)
            .map_err(|e| {
                error!("Failed to save preprocessor: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        info!("Preprocessor saved");
        Ok(save_path)
    }
    /// Load the preprocessor from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Load Preprocessor").entered();
        let _ = span.enter();
        let load_path = path
            .join(SaveName::Preprocessor)
            .with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;
        // Load the data using joblib
        self.preprocessor = joblib
            .call_method("load", (load_path,), kwargs)
            .map_err(|e| {
                error!("Failed to load preprocessor: {}", e);
                OpsmlError::new_err(e.to_string())
            })?
            .into();

        info!("Preprocessor loaded");
        Ok(())
    }
    /// Save the model to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    pub fn save_model(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Save Model").entered();
        let _ = span.enter();

        // check if model is None
        if self.model.is_none(py) {
            error!("No model detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let torch = py.import("torch")?;

        let state_dict = self.model.getattr(py, "state_dict")?.call0(py)?;

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Pt);
        let full_save_path = path.join(&save_path);

        // Save torch model
        torch
            .call_method("save", (state_dict, full_save_path), kwargs)
            .map_err(|e| {
                error!("Failed to save model: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        info!("Model saved");

        Ok(save_path)
    }

    pub fn load_model<'py>(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Load Model");
        let _ = span.enter();

        let load_path = path.join(SaveName::Model).with_extension(Suffix::Pt);
        let torch = py.import("torch")?;

        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());

        // get model from kwargs:
        let model = if let Ok(Some(model)) = kwargs.get_item("model") {
            kwargs.del_item("model")?;
            model
        } else {
            Err(OpsmlError::new_err(
                "TorchModel loading requires model to be passed into model kwargs for loading
                {'model': {{your_model_architecture}}}
                ",
            ))?
        };

        // ensure weights only
        kwargs.set_item("weights_only", true)?;

        let state_dict = torch.call_method("load", (load_path,), Some(&kwargs))?;

        // load state dict
        model.call_method("load_state_dict", (state_dict,), None)?;

        // set model to eval mode
        model.call_method0("eval")?;

        self.model = model.clone().unbind();

        info!("Model loaded");

        Ok(())
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
    pub fn load_data<'py>(
        &mut self,
        py: Python,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Load Data");
        let _ = span.enter();

        // load sample data
        self.sample_data = TorchSampleData::load_data(py, path, &data_type, kwargs)?;

        info!("Sample data loaded");

        Ok(())
    }

    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    pub fn _convert_to_onnx(
        &mut self,
        py: Python,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::INFO, "Converting model to ONNX").entered();
        let _ = span.enter();

        self.onnx_session = Some(OnnxModelConverter::convert_model(
            py,
            self.model.bind(py),
            &self.sample_data,
            &self.model_interface_type,
            &self.model_type,
            kwargs,
        )?);

        info!("Model converted to ONNX");

        Ok(())
    }

    /// Converts the model to onnx
    ///
    /// # Arguments
    ///
    /// * `py` - Link to python interpreter and lifetime
    /// * `kwargs` - Additional kwargs
    ///
    fn _save_onnx_model(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Saving ONNX Model").entered();
        let _ = span.enter();

        if self.onnx_session.is_none() {
            self.convert_to_onnx(py, kwargs)?;
        }

        let save_path = PathBuf::from(SaveName::OnnxModel.to_string()).with_extension(Suffix::Onnx);
        let full_save_path = path.join(&save_path);
        let bytes = self.onnx_session.as_ref().unwrap().model_bytes(py)?;

        fs::write(&full_save_path, bytes)?;

        info!("ONNX model saved");

        Ok(save_path)
    }
}
