use crate::base::parse_save_kwargs;
use crate::model::base::utils::OnnxExtension;
use crate::model::{
    ModelInterface, ModelInterfaceMetadata, ModelInterfaceSaveMetadata, ModelLoadKwargs,
};
use crate::ModelSaveKwargs;
use crate::OnnxSession;
use opsml_error::OpsmlError;
use opsml_types::{ModelInterfaceType, ModelType, TaskType};
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, error, instrument};

use crate::BaseOnnxConverter;

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct OnnxModel;

#[pymethods]
impl OnnxModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<(Self, ModelInterface)> {
        // check if model is an onnxruntime.InferenceSession
        let rt = py
            .import("onnxruntime")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import onnxruntime: {}", e)))?;

        if let Some(model) = model {
            let inference_session = rt.getattr("InferenceSession")?;
            if model.is_instance(&inference_session).map_err(|e| {
                OpsmlError::new_err(format!(
                    "Failed to check if model is an InferenceSession: {}",
                    e
                ))
            })? {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an onnxruntime.InferenceSession",
                ));
            }
        }

        let mut model_interface =
            ModelInterface::new(py, model, sample_data, task_type, drift_profile)?;
        model_interface.interface_type = ModelInterfaceType::Onnx;

        if model_interface.model_type == ModelType::Unknown {
            model_interface.model_type = ModelType::SklearnEstimator;
        }

        // extract and convert to onnx_session
        let onnx_session = if let Some(model) = model {
            let sess = BaseOnnxConverter::get_onnx_session(
                model,
                model_interface
                    .sample_data
                    .get_feature_names(py)
                    .map_err(|e| {
                        OpsmlError::new_err(format!(
                            "Failed to get feature names from sample data: {}",
                            e
                        ))
                    })?,
            )?;

            Some(Py::new(py, sess).map_err(|e| {
                OpsmlError::new_err(format!("Failed to create ONNX session: {}", e))
            })?)
        } else {
            None
        };

        model_interface.onnx_session = onnx_session;

        Ok((OnnxModel {}, model_interface))
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
    #[instrument(skip_all)]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        debug!("Saving model interface {:?}", to_onnx);

        let (onnx_kwargs, _, _) = parse_save_kwargs(py, &save_kwargs);

        let parent = self_.as_super();
        let onnx_model_uri = parent
            .save_onnx_model(py, &path, onnx_kwargs.as_ref())
            .map_err(|e| {
                error!("Failed to save ONNX model. Error: {}", e);
                e
            })?;

        let sample_data_uri = parent.save_data(py, &path, None).map_err(|e| {
            error!("Failed to save sample data. Error: {}", e);
            e
        })?;

        let drift_profile_uri = if parent.drift_profile.is_empty() {
            None
        } else {
            Some(parent.save_drift_profile(py, &path).map_err(|e| {
                error!("Failed to save drift profile. Error: {}", e);
                e
            })?)
        };

        parent.schema = parent.create_feature_schema(py).map_err(|e| {
            error!("Failed to create feature schema. Error: {}", e);
            e
        })?;

        let save_metadata = ModelInterfaceSaveMetadata {
            model_uri: onnx_model_uri.clone(),
            data_processor_map: HashMap::new(),
            sample_data_uri,
            onnx_model_uri: Some(onnx_model_uri),
            drift_profile_uri,
            extra: None,
            save_kwargs,
        };

        let onnx_session = parent.onnx_session.as_ref().map(|sess| {
            let sess = sess.bind(py);
            // extract OnnxSession from py object
            sess.extract::<OnnxSession>().unwrap()
        });

        let metadata = ModelInterfaceMetadata::new(
            save_metadata,
            parent.task_type.clone(),
            parent.model_type.clone(),
            parent.data_type.clone(),
            parent.schema.clone(),
            parent.interface_type.clone(),
            onnx_session,
            HashMap::new(),
            parent.drift_type.clone(),
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
    #[pyo3(signature = (path, metadata, load_kwargs=None, ))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> PyResult<()> {
        let load_kwargs = load_kwargs.unwrap_or_default();

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();

            let onnx_path = path.join(&metadata.model_uri);
            parent.load_onnx_model(py, &onnx_path, load_kwargs.onnx_kwargs(py))?;

            if metadata.drift_profile_uri.is_some() {
                let drift_path = path.join(&metadata.drift_profile_uri.ok_or_else(|| {
                    OpsmlError::new_err("Drift profile URI not found in metadata")
                })?);

                parent.load_drift_profile(py, &drift_path)?;
            }

            if metadata.sample_data_uri.is_some() {
                let sample_data_path =
                    path.join(&metadata.sample_data_uri.ok_or_else(|| {
                        OpsmlError::new_err("Sample data URI not found in metadata")
                    })?);
                parent.load_data(py, &sample_data_path, None)?;
            }
        }

        Ok(())
    }
}

impl OnnxModel {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &ModelInterfaceMetadata,
    ) -> PyResult<Bound<'py, PyAny>> {
        let onnx_interface = OnnxModel {};

        let mut interface =
            ModelInterface::new(py, None, None, Some(metadata.task_type.clone()), None)?;

        interface.schema = metadata.schema.clone();
        interface.data_type = metadata.data_type.clone();
        interface.model_type = metadata.model_type.clone();
        interface.interface_type = metadata.interface_type.clone();

        interface.onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        Py::new(py, (onnx_interface, interface))?.into_bound_py_any(py)
    }
}
