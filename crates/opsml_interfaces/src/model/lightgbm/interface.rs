use crate::base::{parse_save_args, ModelInterfaceSaveMetadata};
use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use crate::{DataProcessor, SampleData, SaveKwargs};
use opsml_error::OpsmlError;
use opsml_types::{CommonKwargs, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, warn};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LightGBMModelInterfaceMetadata {
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
impl LightGBMModelInterfaceMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (task_type, model_type, data_type, modelcard_uid, feature_map, sample_data_interface_type, preprocessor_name, metadata=None))]
    pub fn new(
        task_type: String,
        model_type: String,
        data_type: String,
        modelcard_uid: String,
        feature_map: FeatureSchema,
        sample_data_interface_type: String,
        preprocessor_name: String,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        LightGBMModelInterfaceMetadata {
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
pub struct LightGBMModel {
    #[pyo3(get)]
    pub preprocessor: PyObject,

    #[pyo3(get, set)]
    preprocessor_name: String,
}

#[pymethods]
impl LightGBMModel {
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
            let booster = py.import("lightgbm")?.getattr("Booster")?;

            if model.is_instance(&booster).unwrap() {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an lightgbm booster or inherit from Booster. If
                    using the Sklearn api version of LightGBMModel, use an SklearnModel interface instead",
                ));
            }
        }

        let mut model_interface =
            ModelInterface::new(py, model, sample_data, task_type, schema, drift_profile)?;

        model_interface.model_interface_type = ModelInterfaceType::LightGBM;
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
            LightGBMModel {
                preprocessor,
                preprocessor_name,
            },
            model_interface,
        ))
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
    pub fn load_preprocessor(
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
        py: Python<'py>,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        let super_ = self_.as_ref();
        // check if data is None
        if super_.model.is_none(py) {
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Text);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        super_
            .model
            .call_method(py, "save_model", (full_save_path,), kwargs)?;

        Ok(save_path)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_model<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let super_ = self_.as_super();

        // get sample_data
        super_.sample_data = SampleData::load_data(py, &path, &super_.data_type, kwargs)?;

        let load_path = path.join(SaveName::Model).with_extension(Suffix::Text);

        let booster = py.import("lightgbm")?.getattr("Booster")?;

        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());
        kwargs.set_item("model_file", load_path)?;

        let model = booster.call((), Some(&kwargs))?;

        // Save the data using joblib
        super_.model = model.into();

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
        py: Python<'py>,
        path: PathBuf,
        to_onnx: bool,
        save_args: Option<SaveKwargs>,
    ) -> PyResult<ModelInterfaceSaveMetadata> {
        // parse the save args
        let (onnx_kwargs, model_kwargs) = parse_save_args(py, &save_args);

        debug!(
            "Saving model to: {:?} with save_args: {:?}",
            path, save_args
        );

        // save the preprocessor if it exists
        let preprocessor_entity = if self_.preprocessor.is_none(py) {
            None
        } else {
            let uri = self_.save_preprocessor(
                py,
                path.clone(),
                save_args.as_ref().and_then(|args| args.model_kwargs(py)),
            )?;

            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri,
            })
        };

        let sample_data_uri = self_
            .as_super()
            .sample_data
            .save_data(py, path.clone())
            .unwrap_or_else(|e| {
                warn!("Failed to save sample data. Defaulting to None: {}", e);
                None
            });

        self_.as_super().schema = self_.as_super().create_feature_schema(py)?;

        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(self_.as_super().save_onnx_model(
                py,
                path.clone(),
                onnx_kwargs.as_ref(),
            )?);
        }

        // save drift profile
        let drift_profile_uri = if self_.as_super().drift_profile.is_empty() {
            None
        } else {
            Some(self_.as_super().save_drift_profile(path.clone())?)
        };

        // save model
        let model_uri = LightGBMModel::save_model(self_, py, path.clone(), model_kwargs.as_ref())?;

        // create the data processor map
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
            save_args,
        };

        Ok(metadata)
    }
}
