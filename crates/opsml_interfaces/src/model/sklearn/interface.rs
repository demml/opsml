use crate::base::DataProcessor;
use crate::base::ModelInterfaceMetadata;
use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use crate::ModelType;
use crate::{LoadKwargs, SaveKwargs};
use opsml_error::OpsmlError;
use opsml_types::CommonKwargs;
use opsml_types::{SaveName, Suffix};
use opsml_utils::pyobject_to_json;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::{Path, PathBuf};
use tracing::instrument;
use tracing::{debug, error, info};

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
        model_interface.interface_type = ModelInterfaceType::Sklearn;

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
    #[instrument(skip(self_, py, path, to_onnx, save_kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python<'py>,
        path: PathBuf,
        to_onnx: bool,
        save_kwargs: Option<SaveKwargs>,
    ) -> PyResult<ModelInterfaceMetadata> {
        debug!("Saving model interface");

        // save the preprocessor if it exists
        let preprocessor_entity = if self_.preprocessor.is_none(py) {
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
            })
        };

        // call the super save method
        let mut metadata = self_.as_super().save(py, path, to_onnx, save_kwargs)?;

        // add the preprocessor to the metadata
        preprocessor_entity.map(|preprocessor| {
            metadata
                .save_metadata
                .data_processor_map
                .insert("preprocessor".to_string(), preprocessor)
        });

        let model = self_.as_super().model.as_ref().unwrap().bind(py);
        metadata.model_specific_metadata = SklearnModel::extract_model_params(py, model)?;

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
        // if kwargs is not None, unwrap, else default to None
        let load_kwargs = load_kwargs.unwrap_or_default();

        // parent scope - can only borrow mutable one at a time
        {
            let parent = self_.as_super();
            if model {
                parent.load_model(py, &path, load_kwargs.model_kwargs(py))?;
            }

            if onnx {
                parent.load_onnx_model(py, &path, load_kwargs.onnx_kwargs(py))?;
            }

            if drift_profile {
                parent.load_drift_profile(&path)?;
            }

            if sample_data {
                parent.load_data(py, &path, None)?;
            }
        }

        if preprocessor {
            self_.load_preprocessor(py, &path, load_kwargs.preprocessor_kwargs(py))?;
        }

        Ok(())
    }
}

impl SklearnModel {
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
    ) -> PyResult<PathBuf> {
        // check if data is None
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
        self.preprocessor = joblib.call_method("load", (load_path,), kwargs)?.into();

        Ok(())
    }

    pub fn extract_model_params(
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<serde_json::Value> {
        let new_dict = PyDict::new(py);

        new_dict.set_item("params", model.call_method0("get_params")?)?;
        set_sklearn_model_attribute(model, &new_dict)?;

        Ok(pyobject_to_json(&new_dict).map_err(OpsmlError::new_err)?)
    }
}

enum CommonSklearnAttributes {
    Coef,
    Intercept,
    FeatureImportances,
    NFeaturesIn,
    NClasses,
    NOutputs,
    NTreesPerIteration,
    DoEarlyStopping,
    Niter,
    IsCategorical,
}

impl CommonSklearnAttributes {
    pub fn to_str(&self) -> &str {
        match self {
            CommonSklearnAttributes::Coef => "coef_",
            CommonSklearnAttributes::Intercept => "intercept_",
            CommonSklearnAttributes::FeatureImportances => "feature_importances_",
            CommonSklearnAttributes::NFeaturesIn => "n_features_in_",
            CommonSklearnAttributes::NClasses => "n_classes_",
            CommonSklearnAttributes::NOutputs => "n_outputs_",
            CommonSklearnAttributes::NTreesPerIteration => "n_trees_per_iteration_",
            CommonSklearnAttributes::DoEarlyStopping => "do_early_stopping",
            CommonSklearnAttributes::Niter => "n_iter_",
            CommonSklearnAttributes::IsCategorical => "is_categorical",
        }
    }

    pub fn to_vec() -> Vec<CommonSklearnAttributes> {
        vec![
            CommonSklearnAttributes::Coef,
            CommonSklearnAttributes::Intercept,
            CommonSklearnAttributes::FeatureImportances,
            CommonSklearnAttributes::NFeaturesIn,
            CommonSklearnAttributes::NClasses,
            CommonSklearnAttributes::NOutputs,
            CommonSklearnAttributes::NTreesPerIteration,
            CommonSklearnAttributes::DoEarlyStopping,
            CommonSklearnAttributes::Niter,
            CommonSklearnAttributes::IsCategorical,
        ]
    }
}

pub fn set_sklearn_model_attribute(
    model: &Bound<'_, PyAny>,
    dict: &Bound<'_, PyDict>,
) -> PyResult<()> {
    let attributes = CommonSklearnAttributes::to_vec();

    for attribute in attributes {
        if model.hasattr(attribute.to_str())? {
            dict.set_item(attribute.to_str(), model.getattr(attribute.to_str())?)?;
        }
    }

    Ok(())
}
