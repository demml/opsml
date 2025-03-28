use crate::base::{parse_save_kwargs, ModelInterfaceMetadata, ModelInterfaceSaveMetadata};
use crate::model::ModelInterface;
use crate::types::{FeatureSchema, ProcessorType};
use crate::OnnxSession;
use crate::{DataProcessor, ModelLoadKwargs, ModelSaveKwargs};
use opsml_error::OpsmlError;
use opsml_types::{CommonKwargs, ModelInterfaceType, SaveName, Suffix, TaskType};
use opsml_utils::pyobject_to_json;
use pyo3::gc::PyVisit;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use pyo3::PyTraverseError;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument};

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct LightGBMModel {
    #[pyo3(get)]
    pub preprocessor: Option<PyObject>,

    #[pyo3(get, set)]
    preprocessor_name: String,
}

#[pymethods]
impl LightGBMModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, preprocessor=None, sample_data=None, task_type=None, schema=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        preprocessor: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
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

        let mut model_interface = ModelInterface::new(
            py,
            model,
            sample_data,
            task_type,
            schema,
            drift_profile,
            None,
        )?;

        model_interface.interface_type = ModelInterfaceType::LightGBM;
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
            LightGBMModel {
                preprocessor,
                preprocessor_name,
            },
            model_interface,
        ))
    }

    #[getter]
    pub fn get_preprocessor<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        if self.preprocessor.is_none() {
            None
        } else {
            Some(
                self.preprocessor
                    .as_ref()
                    .unwrap()
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
    #[pyo3(signature = (path, to_onnx=false, save_kwargs=None))]
    #[instrument(skip_all)]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        debug!("Saving lightgbm interface");

        // parse the save args
        let (onnx_kwargs, model_kwargs, preprocessor_kwargs) = parse_save_kwargs(py, &save_kwargs);

        // save the preprocessor if it exists
        let preprocessor_entity = if self_.preprocessor.is_none() {
            None
        } else {
            let uri = self_.save_preprocessor(py, &path, preprocessor_kwargs.as_ref())?;

            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri,
                r#type: ProcessorType::Preprocessor,
            })
        };

        let sample_data_uri = self_.as_super().save_data(py, &path, None)?;
        self_.as_super().create_feature_schema(py)?;

        let mut onnx_model_uri = None;
        if to_onnx {
            onnx_model_uri = Some(self_.as_super().save_onnx_model(
                py,
                &path,
                onnx_kwargs.as_ref(),
            )?);
        }

        let onnx_session = {
            self_.as_super().onnx_session.as_ref().map(|sess| {
                let sess = sess.bind(py);
                // extract OnnxSession from py object
                sess.extract::<OnnxSession>().unwrap()
            })
        };

        // save drift profile
        let drift_profile_uri = if self_.as_super().drift_profile.is_empty() {
            None
        } else {
            Some(self_.as_super().save_drift_profile(py, &path)?)
        };

        // create the data processor map
        let data_processor_map = preprocessor_entity
            .map(|preprocessor| {
                let mut map = HashMap::new();
                map.insert(preprocessor.name.clone(), preprocessor);
                map
            })
            .unwrap_or_default();

        // create save metadata
        let save_metadata = ModelInterfaceSaveMetadata {
            data_processor_map,
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri,
            extra: None,
            save_kwargs,
            ..Default::default()
        };

        // create interface metadata
        let mut metadata = ModelInterfaceMetadata::new(
            save_metadata,
            self_.as_super().task_type.clone(),
            self_.as_super().model_type.clone(),
            self_.as_super().data_type.clone(),
            self_.as_super().schema.clone(),
            self_.as_super().interface_type.clone(),
            onnx_session,
            HashMap::new(),
        );

        // save model (needs to be last because we pass self_ to save_model, which takes ownership)
        let model_uri = LightGBMModel::save_model(self_, py, &path, model_kwargs.as_ref())?;

        metadata.save_metadata.model_uri = model_uri;

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
    /// * `PyResult<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, metadata, onnx=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        metadata: ModelInterfaceSaveMetadata,
        onnx: bool,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> PyResult<()> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        let model_path = path.join(&metadata.model_uri);
        let model = self_.load_model(py, &model_path, load_kwargs.model_kwargs(py))?;
        self_.as_super().model = Some(model);

        if !metadata.data_processor_map.is_empty() {
            // get first key from metadata.save_metadata.data_processor_map.keys() or default to unknow
            let processor = metadata
                .data_processor_map
                .values()
                .next()
                .ok_or_else(|| OpsmlError::new_err("No preprocessor URI found in metadata"))?;

            let preprocessor_uri = path.join(&processor.uri);

            self_.load_preprocessor(py, &preprocessor_uri, load_kwargs.preprocessor_kwargs(py))?;
        }

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();

            if onnx {
                let onnx_path =
                    path.join(&metadata.onnx_model_uri.ok_or_else(|| {
                        OpsmlError::new_err("ONNX model URI not found in metadata")
                    })?);
                parent.load_onnx_model(py, &onnx_path, load_kwargs.onnx_kwargs(py))?;
            }

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

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref preprocessor) = self.preprocessor {
            visit.call(preprocessor)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.preprocessor = None;
    }
}

impl LightGBMModel {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &ModelInterfaceMetadata,
    ) -> PyResult<Bound<'py, PyAny>> {
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

        let lightgbm_interface = LightGBMModel {
            preprocessor: None,
            preprocessor_name,
        };

        let mut interface = ModelInterface::new(
            py,
            None,
            None,
            Some(metadata.task_type.clone()),
            Some(metadata.schema.clone()),
            None,
            None,
        )?;

        interface.data_type = metadata.data_type.clone();
        interface.model_type = metadata.model_type.clone();
        interface.interface_type = metadata.interface_type.clone();

        // convert onnx session to to Py<OnnxSession>
        interface.onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        Py::new(py, (lightgbm_interface, interface))?.into_bound_py_any(py)
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
    ) -> PyResult<PathBuf> {
        // check if data is None
        if self.preprocessor.is_none() {
            error!("No preprocessor detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
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
    pub fn save_model<'py>(
        self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        let super_ = self_.as_ref();

        if super_.model.is_none() {
            error!("No model detected in interface for saving");
            return Err(OpsmlError::new_err(
                "No model detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Text);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        super_
            .model
            .as_ref()
            .unwrap()
            .call_method(py, "save_model", (full_save_path,), kwargs)?;

        debug!("Model saved");
        Ok(save_path)
    }

    /// Load the model from a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the model from
    /// * `kwargs` - Additional keyword arguments to pass to the load
    ///
    /// # Returns
    ///
    /// * `PyResult<()>` - Result of the load
    #[instrument(skip_all)]
    pub fn load_model<'py>(
        &self,
        py: Python<'py>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PyObject> {
        let booster = py.import("lightgbm")?.getattr("Booster")?;

        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());
        kwargs.set_item("model_file", path)?;

        let model = booster.call((), Some(&kwargs)).map_err(|e| {
            error!("Failed to load model from file: {}", e);
            OpsmlError::new_err(format!("Failed to load model from file: {}", e))
        })?;

        debug!("Model loaded");

        model.into_py_any(py)
    }

    pub fn extract_model_params(
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<serde_json::Value> {
        let new_dict = PyDict::new(py);

        new_dict.set_item("params", model.call_method0("get_params")?)?;
        set_lightgbm_model_attribute(model, &new_dict)?;

        pyobject_to_json(&new_dict).map_err(OpsmlError::new_err)
    }
}

enum CommonLightGBMAttributes {
    BestScore,
    FeatureImportances,
    FeatureNames,
    FeatureNamesIn,
    NEstimators,
    NIter,
    Objective,
    NClasses,
    Classes,
}

impl CommonLightGBMAttributes {
    pub fn to_str(&self) -> &str {
        match self {
            CommonLightGBMAttributes::BestScore => "best_score_",
            CommonLightGBMAttributes::FeatureImportances => "feature_importances_",
            CommonLightGBMAttributes::FeatureNames => "feature_name_",
            CommonLightGBMAttributes::FeatureNamesIn => "feature_names_in_",
            CommonLightGBMAttributes::NEstimators => "n_estimators_",
            CommonLightGBMAttributes::NIter => "n_iter_",
            CommonLightGBMAttributes::Objective => "objective_",
            CommonLightGBMAttributes::NClasses => "n_classes_",
            CommonLightGBMAttributes::Classes => "classes_",
        }
    }

    pub fn to_vec() -> Vec<CommonLightGBMAttributes> {
        vec![
            CommonLightGBMAttributes::BestScore,
            CommonLightGBMAttributes::FeatureImportances,
            CommonLightGBMAttributes::FeatureNames,
            CommonLightGBMAttributes::FeatureNamesIn,
            CommonLightGBMAttributes::NEstimators,
            CommonLightGBMAttributes::NIter,
            CommonLightGBMAttributes::Objective,
            CommonLightGBMAttributes::NClasses,
            CommonLightGBMAttributes::Classes,
        ]
    }
}

pub fn set_lightgbm_model_attribute(
    model: &Bound<'_, PyAny>,
    dict: &Bound<'_, PyDict>,
) -> PyResult<()> {
    let attributes = CommonLightGBMAttributes::to_vec();

    for attribute in attributes {
        if model.hasattr(attribute.to_str())? {
            dict.set_item(attribute.to_str(), model.getattr(attribute.to_str())?)?;
        }
    }

    Ok(())
}
