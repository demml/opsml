use crate::base::ModelInterfaceSaveMetadata;
use crate::base::Processor;
use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use crate::SaveArgs;
use opsml_error::OpsmlError;
use opsml_types::CommonKwargs;
use opsml_types::{SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SklearnModelInterfaceMetadata {
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
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl SklearnModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: FeatureSchema,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        SklearnModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            modelcard_uid,
            feature_map,
            sample_data_interface_type,
            preprocessor_name,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct SklearnModel {
    #[pyo3(get)]
    pub preprocessor: PyObject,

    #[pyo3(get, set)]
    preprocessor_name: String,
}

#[pymethods]
impl SklearnModel {
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
            let base_estimator = py
                .import("sklearn")?
                .getattr("base")?
                .getattr("BaseEstimator")?;
            if model.is_instance(&base_estimator).unwrap() {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Sample data must be an sklearn model and inherit from BaseEstimator",
                ));
            }
        }

        let mut model_interface =
            ModelInterface::new(py, model, sample_data, task_type, schema, drift_profile)?;
        model_interface.model_interface_type = ModelInterfaceType::Sklearn;

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
            SklearnModel {
                preprocessor,
                preprocessor_name,
            },
            model_interface,
        ))
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
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None
        if self.preprocessor.is_none(py) {
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Preprocessor).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method("dump", (&self.preprocessor, full_save_path), kwargs)?;

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
    pub fn load_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path
            .join(SaveName::Preprocessor)
            .with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.preprocessor = joblib.call_method("load", (load_path,), kwargs)?.into();

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
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        to_onnx: bool,
        save_args: Option<SaveArgs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // save the preprocessor if it exists
        let preprocessor_entity = if self_.preprocessor.is_none(py) {
            None
        } else {
            let uri = self_.save_preprocessor(
                py,
                path.clone(),
                save_args.as_ref().and_then(|args| args.model_kwargs(py)),
            )?;

            Some(Processor {
                name: self_.preprocessor_name.clone(),
                uri: uri,
            })
        };

        // call the super save method
        let mut metadata = self_.as_super().save(py, path, to_onnx, save_args)?;

        // add the preprocessor to the metadata
        preprocessor_entity.map(|preprocessor| {
            metadata
                .data_processor_map
                .insert("preprocessor".to_string(), preprocessor)
        });

        Ok(metadata)
    }
}
