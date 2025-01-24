use crate::base::{parse_save_kwargs, ModelInterfaceSaveMetadata};
use crate::model::torch::types::{TorchOnnxArgs, TorchSaveArgs};
use crate::model::torch::TorchSampleData;
use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use crate::{DataProcessor, SampleData, SaveKwargs};
use opsml_error::OpsmlError;
use opsml_types::{CommonKwargs, SaveName, Suffix};
use ort::info;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, error, info, span, warn, Level};

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
    pub feature_map: FeatureSchema,
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
        feature_map: FeatureSchema,
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

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct TorchModel {
    #[pyo3(get)]
    pub preprocessor: PyObject,

    #[pyo3(get, set)]
    preprocessor_name: String,

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
        if let Some(model) = model {
            let torch_module = py.import("torch")?.getattr("nn")?.getattr("Module")?;
            if model.is_instance(&torch_module).unwrap() {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an instance of torch.nn.Module",
                ));
            }
        }
        let mut model_interface =
            ModelInterface::new(py, model, None, task_type, schema, drift_profile)?;

        // override ModelInterface SampleData with TorchSampleData
        let sample_data = match sample_data {
            // attempt to create sample data. If it fails, return default sample data and log a warning
            Some(data) => TorchSampleData::new(data).unwrap_or_else(|e| {
                warn!("Failed to create sample data. Defaulting to None: {}", e);
                TorchSampleData::default()
            }),
            None => TorchSampleData::default(),
        };

        model_interface.model_interface_type = ModelInterfaceType::Torch;
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
            },
            model_interface,
        ))
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
    /// Save the preprocessor to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[pyo3(signature = (path, **kwargs))]
    pub fn save_preprocessor(
        &self,
        py: Python,
        path: PathBuf,
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
    #[pyo3(signature = (path, **kwargs))]
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: PathBuf,
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
    #[pyo3(signature = (path, **kwargs))]
    pub fn save_model<'py>(
        self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        let span = span!(Level::INFO, "Save Model").entered();
        let _ = span.enter();
        let super_ = self_.as_ref();

        // check if model is None
        if super_.model.is_none(py) {
            error!("No model detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let torch = py.import("torch")?;

        // TOrch can be saved as a model or as a state dict
        let save_as_state_dict = kwargs.map_or(false, |kwargs| {
            kwargs
                .get_item("save_as_state_dict")
                .unwrap()
                .map_or(false, |item| item.extract::<bool>().unwrap_or(false))
        });

        let model = if save_as_state_dict {
            super_.model.getattr(py, "state_dict")?.call0(py)?
        } else {
            super_.model.clone_ref(py)
        };

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Pt);
        let full_save_path = path.join(&save_path);

        // Save torch model
        torch
            .call_method("save", (model, full_save_path), kwargs)
            .map_err(|e| {
                error!("Failed to save model: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        info!("Model saved");

        Ok(save_path)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_model<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let span = span!(Level::DEBUG, "Load Model");
        let _ = span.enter();

        let super_ = self_.as_super();

        let load_path = path.join(SaveName::Model).with_extension(Suffix::Json);
        let booster = py.import("xgboost")?.getattr("Booster")?;
        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());
        kwargs.set_item("model_file", load_path)?;
        let model = booster.call((), Some(&kwargs)).map_err(|e| {
            error!("Failed to load model: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;
        // Save the data using joblib
        super_.model = model.into();
        Ok(())
    }

    /// Saves the sample data
    #[pyo3(signature = (path))]
    pub fn save_data(&self, py: Python, path: PathBuf) -> PyResult<Option<PathBuf>> {
        // if sample_data is not None, save the sample data
        let sample_data_uri = self.sample_data.save_data(py, &path).unwrap_or_else(|e| {
            warn!("Failed to save sample data. Defaulting to None: {}", e);
            None
        });

        Ok(sample_data_uri)
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
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // color text
        let span = span!(Level::INFO, "Saving TorchModel interface").entered();
        let _ = span.enter();

        // parse the save args
        let (onnx_kwargs, _model_kwargs, preprocessor_kwargs) = parse_save_kwargs(py, &save_kwargs);
        let preprocessor_entity = if self_.preprocessor.is_none(py) {
            None
        } else {
            let uri = self_.save_preprocessor(py, path.clone(), preprocessor_kwargs.as_ref())?;
            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri: uri,
            })
        };
        let sample_data_uri = self_.save_data(py, path.clone())?;
        self_.as_super().schema = self_.as_super().create_feature_schema(py)?;

        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(self_.as_super().save_onnx_model(
                py,
                path.clone(),
                onnx_kwargs.as_ref(),
            )?);
        }

        let drift_profile_uri = if self_.as_super().drift_profile.is_empty() {
            None
        } else {
            Some(self_.as_super().save_drift_profile(path.clone())?)
        };

        let model_uri = TorchModel::save_model(self_, py, path.clone(), None)?;

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
}
