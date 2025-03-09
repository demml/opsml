use crate::base::{parse_save_kwargs, ModelInterfaceMetadata, ModelInterfaceSaveMetadata};
use crate::model::ModelInterface;
use crate::types::FeatureSchema;
use crate::{DataProcessor, ModelLoadKwargs, ModelSaveKwargs};
use crate::{OnnxSession, ProcessorType};
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
use tracing::{debug, error, info, instrument};

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct CatBoostModel {
    #[pyo3(get)]
    pub preprocessor: Option<PyObject>,

    #[pyo3(get, set)]
    preprocessor_name: String,

    model_name: String,
}

#[pymethods]
impl CatBoostModel {
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
        let mut model_name = CommonKwargs::Undefined.to_string();
        // check if model is base estimator for sklearn validation
        if let Some(model) = model {
            let boost = py.import("catboost")?.getattr("CatBoost")?;

            if model.is_instance(&boost).unwrap() {
                model_name = model.getattr("__class__")?.getattr("__name__")?.to_string();
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an CatBoost model or inherit from CatBoost",
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

        model_interface.interface_type = ModelInterfaceType::CatBoost;
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
            CatBoostModel {
                preprocessor,
                preprocessor_name,
                model_name,
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
    #[instrument(skip(self_, py, path, to_onnx, save_kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        debug!("Saving CatBoost interface");

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

        self_.as_super().schema = self_.as_super().create_feature_schema(py)?;

        let mut onnx_model_uri = None;
        if to_onnx {
            // bypassing save_onnx_model to avoid duplicate saving (catboost saves onnx model)
            let save_path =
                PathBuf::from(SaveName::OnnxModel.to_string()).with_extension(Suffix::Onnx);
            let full_save_path = path.join(&save_path);

            self_
                .as_super()
                .convert_to_onnx(py, &full_save_path, onnx_kwargs.as_ref())?;

            onnx_model_uri = Some(save_path);
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
        let mut extra = HashMap::new();
        extra.insert("model_name".to_string(), self_.model_name.clone());

        let mut metadata = ModelInterfaceMetadata::new(
            save_metadata,
            self_.as_super().task_type.clone(),
            self_.as_super().model_type.clone(),
            self_.as_super().data_type.clone(),
            self_.as_super().schema.clone(),
            self_.as_super().interface_type.clone(),
            onnx_session,
            extra,
        );

        // save model
        let model_uri = CatBoostModel::save_model(self_, py, &path, model_kwargs.as_ref())?;

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
    /// * `PyResult<DataInterfaceMetadata>` - DataInterfaceMetadata
    #[pyo3(signature = (path, onnx=false, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        onnx: bool,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> PyResult<()> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        let model = self_.load_model(py, &path, load_kwargs.model_kwargs(py))?;
        self_.as_super().model = Some(model);

        self_.load_preprocessor(py, &path, load_kwargs.preprocessor_kwargs(py))?;

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();

            if onnx {
                parent.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
            }

            parent.load_drift_profile(py, &path)?;
            parent.load_data(py, &path, None)?;
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

impl CatBoostModel {
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

        // convert onnx session to to Py<OnnxSession>
        let onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        let model_name = metadata
            .extra_metadata
            .get("model_name")
            .unwrap_or(&"".to_string())
            .clone();

        let model_interface = CatBoostModel {
            preprocessor: None,
            preprocessor_name,
            model_name,
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
        interface.onnx_session = onnx_session;

        Py::new(py, (model_interface, interface))?.into_bound_py_any(py)
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
    #[instrument(skip_all)]
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path
            .join(SaveName::Preprocessor)
            .with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        let preprocessor = joblib.call_method("load", (load_path,), kwargs)?;

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
    #[instrument(skip(self_, py, path, kwargs))]
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

        let save_path = PathBuf::from(SaveName::Model).with_extension(Suffix::Catboost);
        let full_save_path = path.join(&save_path);

        // Save the data using joblib
        super_
            .model
            .as_ref()
            .unwrap()
            .call_method(py, "save_model", (full_save_path,), kwargs)?;

        info!("Model saved");
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
    ///
    #[instrument(skip_all)]
    pub fn load_model<'py>(
        &self,
        py: Python<'py>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Model).with_extension(Suffix::Catboost);

        let booster = py.import("catboost")?;
        let catboost = booster.getattr("CatBoost")?;

        let model = booster
            .getattr(self.model_name.clone())
            .unwrap_or(catboost)
            .call0()?;

        Ok(model
            .call_method("load_model", (load_path,), kwargs)?
            .unbind())
    }

    pub fn extract_model_params(
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<serde_json::Value> {
        let new_dict = PyDict::new(py);

        new_dict.set_item(
            "params",
            model
                .call_method0("get_all_params")
                .unwrap_or("__missing__".to_string().into_bound_py_any(py)?),
        )?;
        new_dict.set_item(
            "model_name",
            model.getattr("__class__")?.getattr("__name__")?,
        )?;
        set_catboost_model_attribute(model, &new_dict)?;

        pyobject_to_json(&new_dict).map_err(OpsmlError::new_err)
    }
}

enum CommonCatBoostAttributes {
    TreeCount,
    FeatureImportances,
    LearningRate,
    FeatureNames,
    BestScore,
    Classes,
}

impl CommonCatBoostAttributes {
    pub fn to_str(&self) -> &str {
        match self {
            CommonCatBoostAttributes::TreeCount => "tree_count_",
            CommonCatBoostAttributes::FeatureImportances => "feature_importances_",
            CommonCatBoostAttributes::LearningRate => "learning_rate_",
            CommonCatBoostAttributes::FeatureNames => "feature_names_",
            CommonCatBoostAttributes::BestScore => "best_score_",
            CommonCatBoostAttributes::Classes => "classes_",
        }
    }

    pub fn to_vec() -> Vec<CommonCatBoostAttributes> {
        vec![
            CommonCatBoostAttributes::TreeCount,
            CommonCatBoostAttributes::FeatureImportances,
            CommonCatBoostAttributes::LearningRate,
            CommonCatBoostAttributes::FeatureNames,
            CommonCatBoostAttributes::BestScore,
            CommonCatBoostAttributes::Classes,
        ]
    }
}

pub fn set_catboost_model_attribute(
    model: &Bound<'_, PyAny>,
    dict: &Bound<'_, PyDict>,
) -> PyResult<()> {
    let attributes = CommonCatBoostAttributes::to_vec();

    for attribute in attributes {
        if model.hasattr(attribute.to_str())? {
            dict.set_item(attribute.to_str(), model.getattr(attribute.to_str())?)?;
        }
    }

    Ok(())
}
