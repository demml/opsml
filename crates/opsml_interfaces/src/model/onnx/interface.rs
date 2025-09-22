use crate::base::parse_save_kwargs;
use crate::error::ModelInterfaceError;
use crate::model::base::utils::OnnxExtension;
use crate::model::{
    ModelInterface, ModelInterfaceMetadata, ModelInterfaceSaveMetadata, ModelLoadKwargs,
};
use crate::ModelSaveKwargs;
use crate::OnnxSession;
use opsml_types::{ModelInterfaceType, ModelType, TaskType};
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, instrument, warn};

use crate::OnnxModelConverter;

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct OnnxModel {}

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
    ) -> Result<(Self, ModelInterface), ModelInterfaceError> {
        let onnx = py.import("onnx")?;
        if let Some(model) = model {
            let has_serialize = model.hasattr("SerializeToString")?;
            if !has_serialize {
                return Err(ModelInterfaceError::OnnxModelTypeError);
            }
        }

        let version = onnx.getattr("__version__")?.extract::<String>().ok();

        let mut model_interface =
            ModelInterface::new(py, None, sample_data, task_type, drift_profile, version)?;

        model_interface.interface_type = ModelInterfaceType::Onnx;
        model_interface.model_type = ModelType::Onnx;

        // extract and convert to onnx_session
        let onnx_session = if let Some(model) = model {
            let sess = OnnxModelConverter::get_onnx_session(
                model,
                model_interface.sample_data.get_feature_names(py)?,
            )?;

            Some(Py::new(py, sess)?)
        } else {
            None
        };

        model_interface.onnx_session = onnx_session;

        Ok((OnnxModel {}, model_interface))
    }

    /// Get the ONNX session from the parent class
    #[getter]
    pub fn get_session<'py>(
        self_: PyRef<'py, Self>,
        py: Python<'py>,
    ) -> Result<Bound<'py, OnnxSession>, ModelInterfaceError> {
        let parent = self_.as_super();
        if let Some(session) = &parent.onnx_session {
            Ok(session.bind(py).clone())
        } else {
            Err(ModelInterfaceError::OnnxSessionMissing)
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
    #[instrument(skip_all)]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Result<ModelInterfaceMetadata, ModelInterfaceError> {
        debug!("Saving OnnxModel interface");

        let kwargs = parse_save_kwargs(py, save_kwargs.as_ref());

        let parent = self_.as_super();
        let onnx_model_uri = parent.save_onnx_model(py, &path, kwargs.onnx.as_ref())?;

        let sample_data_uri = parent.save_data(py, &path, None)?;

        let drift_profile_uri_map = if parent.drift_profile.is_empty() {
            None
        } else {
            Some(parent.save_drift_profile(py, &path)?)
        };

        parent.schema = parent.create_feature_schema(py)?;

        let save_metadata = ModelInterfaceSaveMetadata {
            model_uri: onnx_model_uri.clone(),
            data_processor_map: HashMap::new(),
            sample_data_uri,
            onnx_model_uri: Some(onnx_model_uri),
            drift_profile_uri_map,
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
            parent.version.clone(),
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
    ) -> Result<(), ModelInterfaceError> {
        let load_kwargs = load_kwargs.unwrap_or_default();

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();

            let onnx_path = path.join(&metadata.model_uri);
            parent.load_onnx_model(py, &onnx_path, load_kwargs.onnx_kwargs(py))?;

            if let Some(ref drift_map) = metadata.drift_profile_uri_map {
                parent.load_drift_profile(py, &path, drift_map)?;
            }

            if metadata.sample_data_uri.is_some() {
                let sample_data_path = path.join(
                    &metadata
                        .sample_data_uri
                        .ok_or_else(|| ModelInterfaceError::MissingSampleDataUriError)?,
                );
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
    ) -> Result<Bound<'py, PyAny>, ModelInterfaceError> {
        let onnx_interface = OnnxModel {};

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
        interface.model_type = metadata.model_type.clone();
        interface.interface_type = metadata.interface_type.clone();

        interface.onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        let interface = Py::new(py, (onnx_interface, interface))?.into_bound_py_any(py)?;

        Ok(interface)
    }
}
