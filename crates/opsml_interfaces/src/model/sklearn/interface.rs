use crate::base::DataProcessor;
use crate::base::ModelInterfaceMetadata;
use crate::error::ModelInterfaceError;
use crate::model::ModelInterface;
use crate::types::ProcessorType;
use crate::ModelInterfaceSaveMetadata;
use crate::OnnxSession;
use crate::{ModelLoadKwargs, ModelSaveKwargs};
use opsml_types::CommonKwargs;
use opsml_types::{ModelInterfaceType, ModelType, TaskType};
use opsml_types::{SaveName, Suffix};
use opsml_utils::pydict_to_json_value;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use pyo3::{PyTraverseError, PyVisit};
use std::path::{Path, PathBuf};
use tracing::debug;
use tracing::{error, instrument};

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct SklearnModel {
    #[pyo3(get)]
    pub preprocessor: Option<Py<PyAny>>,

    #[pyo3(get, set)]
    preprocessor_name: String,
}

#[pymethods]
impl SklearnModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, preprocessor=None, sample_data=None, task_type=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        preprocessor: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> Result<(Self, ModelInterface), ModelInterfaceError> {
        let sklearn = py.import("sklearn")?;
        // check if model is base estimator for sklearn validation
        if let Some(model) = model {
            let base_estimator = sklearn.getattr("base")?.getattr("BaseEstimator")?;
            if model.is_instance(&base_estimator).unwrap() {
                //
            } else {
                return Err(ModelInterfaceError::SklearnTypeError);
            }
        }

        let sklearn_version = sklearn.getattr("__version__")?.extract::<String>().ok();

        let mut model_interface = ModelInterface::new(
            py,
            model,
            sample_data,
            task_type,
            drift_profile,
            sklearn_version,
        )?;
        model_interface.interface_type = ModelInterfaceType::Sklearn;
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

        if model_interface.model_type == ModelType::Unknown {
            model_interface.model_type = ModelType::SklearnEstimator;
        }

        Ok((
            SklearnModel {
                preprocessor,
                preprocessor_name,
            },
            model_interface,
        ))
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
        preprocessor: Option<&Bound<'py, PyAny>>,
    ) -> Result<(), ModelInterfaceError> {
        if let Some(preprocessor) = preprocessor {
            let preprocessor_name = preprocessor
                .getattr("__class__")?
                .getattr("__name__")?
                .to_string();

            self.preprocessor = Some(preprocessor.into_py_any(py)?);
            self.preprocessor_name = preprocessor_name;
            Ok(())
        } else {
            self.preprocessor = None;
            self.preprocessor_name = CommonKwargs::Undefined.to_string();
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
    /// * `Result<DataInterfaceSaveMetadata>` - DataInterfaceSaveMetadata
    #[pyo3(signature = (path, save_kwargs=None))]
    #[instrument(skip_all)]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Result<ModelInterfaceMetadata, ModelInterfaceError> {
        debug!("Saving sklearn model interface");

        // save the preprocessor if it exists
        let preprocessor_entity = if self_.preprocessor.is_none() {
            None
        } else {
            let uri = self_.save_preprocessor(
                py,
                &path,
                save_kwargs.as_ref().and_then(|args| args.model_kwargs(py)),
            )?;

            Some(DataProcessor {
                name: self_.preprocessor_name.clone(),
                uri,
                r#type: ProcessorType::Preprocessor,
            })
        };

        // call the super save method
        debug!("Saving and extracting metadata");
        let mut metadata = self_.as_super().save(py, path, save_kwargs)?;

        // add the preprocessor to the metadata
        preprocessor_entity.map(|preprocessor| {
            debug!("Adding preprocessor to metadata");
            metadata
                .save_metadata
                .data_processor_map
                .insert("preprocessor".to_string(), preprocessor)
        });

        debug!("Setting model");
        let model = self_.as_super().model.as_ref().unwrap().bind(py);

        debug!("Extracting model params");
        metadata.model_specific_metadata = SklearnModel::extract_model_params(py, model)?;

        // add check mark for done
        debug!("Sklearn model interface saved successfully");
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
    /// * `Result<DataInterfaceMetadata>` - DataInterfaceMetadata
    #[pyo3(signature = (path, metadata, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    #[instrument(skip_all, name = "load_sklearn")]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> Result<(), ModelInterfaceError> {
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();
            let model_path = path.join(&metadata.model_uri);

            debug!("loading model");
            parent.load_model(py, &model_path, load_kwargs.model_kwargs(py))?;

            if load_kwargs.load_onnx {
                debug!("loading onnx model");
                let onnx_path = path.join(
                    &metadata
                        .onnx_model_uri
                        .ok_or_else(|| ModelInterfaceError::MissingOnnxUriError)?,
                );
                parent.load_onnx_model(py, &onnx_path, load_kwargs.onnx_kwargs(py))?;
            }

            debug!("loading drift map");
            if let Some(ref drift_map) = metadata.drift_profile_uri_map {
                parent.load_drift_profile(py, &path, drift_map)?;
            }

            debug!("loading sample data");
            if metadata.sample_data_uri.is_some() {
                let sample_data_path = path.join(
                    &metadata
                        .sample_data_uri
                        .ok_or_else(|| ModelInterfaceError::MissingSampleDataUriError)?,
                );
                parent.load_data(py, &sample_data_path, None)?;
            }
        }

        if !metadata.data_processor_map.is_empty() {
            // get first key from metadata.save_metadata.data_processor_map.keys() or default to unknown
            debug!("loading preprocessor");
            let processor = metadata
                .data_processor_map
                .values()
                .next()
                .ok_or_else(|| ModelInterfaceError::MissingPreprocessorUriError)?;

            let preprocessor_uri = path.join(&processor.uri);

            self_.load_preprocessor(py, &preprocessor_uri, load_kwargs.preprocessor_kwargs(py))?;
        }

        Ok(())
    }

    pub fn __str__(self_: PyRef<'_, Self>, py: Python) -> String {
        let onnx_session_json = self_
            .as_super()
            .onnx_session
            .as_ref()
            .map(|session| {
                let sess = session.extract::<OnnxSession>(py).unwrap();
                serde_json::to_value(sess).unwrap_or_default()
            })
            .unwrap_or_default();

        let json = serde_json::json!({
            "preprocessor": self_.preprocessor_name,
            "data_type": self_.as_super().data_type,
            "task_type": self_.as_super().task_type,
            "model_type": self_.as_super().model_type,
            "schema": self_.as_super().schema,
            "interface_type": self_.as_super().interface_type,
            "onnx_session": onnx_session_json,
        });

        PyHelperFuncs::__str__(json)
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

impl SklearnModel {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &ModelInterfaceMetadata,
    ) -> Result<Bound<'py, PyAny>, ModelInterfaceError> {
        // get first key from metadata.save_metadata.data_processor_map.keys() or default to unknow
        let preprocessor_name = metadata
            .save_metadata
            .data_processor_map
            .keys()
            .next()
            .unwrap_or(&CommonKwargs::Undefined.to_string())
            .to_string();
        let sklearn_interface = SklearnModel {
            preprocessor: None,
            preprocessor_name,
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
        interface.model_type = metadata.model_type.clone();
        interface.interface_type = metadata.interface_type.clone();

        // convert onnx session to to Py<OnnxSession>
        interface.onnx_session = metadata
            .onnx_session
            .as_ref()
            .map(|session| Py::new(py, session.clone()).unwrap());

        let interface = Py::new(py, (sklearn_interface, interface))?.into_bound_py_any(py)?;
        Ok(interface)
    }

    /// Save the preprocessor to a file
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the model to
    /// * `kwargs` - Additional keyword arguments to pass to the save
    ///
    #[instrument(skip(self, py, path, kwargs))]
    pub fn save_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, ModelInterfaceError> {
        // check if data is None
        if self.preprocessor.is_none() {
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
    pub fn load_preprocessor(
        &mut self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), ModelInterfaceError> {
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.preprocessor = Some(joblib.call_method("load", (path,), kwargs)?.unbind());

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn extract_model_params(
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> Result<serde_json::Value, ModelInterfaceError> {
        let new_dict = PyDict::new(py);

        new_dict.set_item("params", model.call_method0("get_params")?)?;
        set_sklearn_model_attribute(model, &new_dict)?;

        let value = pydict_to_json_value(py, &new_dict).inspect_err(|e| {
            error!("Failed to serialize sklearn model params: {e}");
        })?;

        Ok(value)
    }
}

enum CommonSklearnAttributes {
    Coef,
    Intercept,
    FeatureImportances,
    FeatureNamesIn,
    NFeaturesIn,
    NClasses,
    NOutputs,
    NTreesPerIteration,
    DoEarlyStopping,
    Niter,
    IsCategorical,
    BestScore,
    NEstimators,
    Classes,
    Objective,
}

impl CommonSklearnAttributes {
    pub fn to_str(&self) -> &str {
        match self {
            CommonSklearnAttributes::Coef => "coef_",
            CommonSklearnAttributes::Intercept => "intercept_",
            CommonSklearnAttributes::FeatureImportances => "feature_importances_",
            CommonSklearnAttributes::NFeaturesIn => "n_features_in_",
            CommonSklearnAttributes::FeatureNamesIn => "feature_names_in_",
            CommonSklearnAttributes::NClasses => "n_classes_",
            CommonSklearnAttributes::NOutputs => "n_outputs_",
            CommonSklearnAttributes::NTreesPerIteration => "n_trees_per_iteration_",
            CommonSklearnAttributes::DoEarlyStopping => "do_early_stopping",
            CommonSklearnAttributes::Niter => "n_iter_",
            CommonSklearnAttributes::IsCategorical => "is_categorical",
            CommonSklearnAttributes::BestScore => "best_score_",
            CommonSklearnAttributes::NEstimators => "n_estimators_",
            CommonSklearnAttributes::Classes => "classes_",
            CommonSklearnAttributes::Objective => "objective_",
        }
    }

    pub fn to_vec() -> Vec<CommonSklearnAttributes> {
        vec![
            CommonSklearnAttributes::Coef,
            CommonSklearnAttributes::Intercept,
            CommonSklearnAttributes::FeatureImportances,
            CommonSklearnAttributes::FeatureNamesIn,
            CommonSklearnAttributes::NFeaturesIn,
            CommonSklearnAttributes::NClasses,
            CommonSklearnAttributes::NOutputs,
            CommonSklearnAttributes::NTreesPerIteration,
            CommonSklearnAttributes::DoEarlyStopping,
            CommonSklearnAttributes::Niter,
            CommonSklearnAttributes::IsCategorical,
            CommonSklearnAttributes::BestScore,
            CommonSklearnAttributes::NEstimators,
            CommonSklearnAttributes::Classes,
            CommonSklearnAttributes::Objective,
        ]
    }
}

pub fn set_sklearn_model_attribute(
    model: &Bound<'_, PyAny>,
    dict: &Bound<'_, PyDict>,
) -> Result<(), ModelInterfaceError> {
    let attributes = CommonSklearnAttributes::to_vec();

    for attribute in attributes {
        if model.hasattr(attribute.to_str())? {
            dict.set_item(attribute.to_str(), model.getattr(attribute.to_str())?)?;
        }
    }

    Ok(())
}
