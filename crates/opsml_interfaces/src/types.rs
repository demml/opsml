use opsml_error::OpsmlError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct Feature {
    #[pyo3(get, set)]
    feature_type: String,
    #[pyo3(get, set)]
    shape: Vec<usize>,
    #[pyo3(get, set)]
    extra_args: HashMap<String, String>,
}

#[pymethods]
impl Feature {
    #[new]
    #[pyo3(signature = (feature_type, shape, extra_args=None))]
    pub fn new(
        feature_type: String,
        shape: Vec<usize>,
        extra_args: Option<HashMap<String, String>>,
    ) -> Self {
        Feature {
            feature_type,
            shape,
            extra_args: extra_args.unwrap_or_default(),
        }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct FeatureSchema {
    #[pyo3(get, set)]
    pub items: HashMap<String, Feature>,
}

#[pymethods]
impl FeatureSchema {
    #[new]
    #[pyo3(signature = (items=None))]
    pub fn new(items: Option<HashMap<String, Feature>>) -> Self {
        FeatureSchema {
            items: items.unwrap_or_default(),
        }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn __getitem__(&self, key: &str) -> PyResult<Feature> {
        match self.items.get(key) {
            Some(value) => Ok(value.clone()),
            None => Err(OpsmlError::new_err(format!(
                "KeyError: key '{}' not found in FeatureMap",
                key
            ))),
        }
    }
}

impl FromIterator<(String, Feature)> for FeatureSchema {
    fn from_iter<I: IntoIterator<Item = (String, Feature)>>(iter: I) -> Self {
        let mut items = HashMap::new();
        for (key, value) in iter {
            items.insert(key, value);
        }
        FeatureSchema { items }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum ModelInterfaceType {
    #[default]
    Base,
    Sklearn,
    CatBoost,
    HuggingFace,
    LightGBM,
    Lightning,
    Torch,
    TensorFlow,
    VowpalWabbit,
    XGBoost,
}

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum ModelType {
    Transformers,
    SklearnPipeline,
    SklearnEstimator,
    StackingRegressor,
    StackingClassifier,
    StackingEstimator,
    CalibratedClassifier,
    LgbmRegressor,
    LgbmClassifier,
    XgbRegressor,
    XgbClassifier,
    XgbBooster,
    LgbmBooster,
    TfKeras,
    Pytorch,
    PytorchLightning,
    Catboost,
    Vowpal,
}

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceModuleType {
    PretrainedModel,
    TransformerModel,
    TransformerPipeline,
}

pub const SKLEARN_SUPPORTED_MODEL_TYPES: &[ModelType] = &[
    ModelType::SklearnEstimator,
    ModelType::StackingRegressor,
    ModelType::StackingClassifier,
    ModelType::SklearnPipeline,
    ModelType::LgbmRegressor,
    ModelType::LgbmClassifier,
    ModelType::XgbRegressor,
    ModelType::CalibratedClassifier,
];

pub const LIGHTGBM_SUPPORTED_MODEL_TYPES: &[ModelType] = &[ModelType::LgbmBooster];

pub const UPDATE_REGISTRY_MODELS: &[ModelType] = &[
    ModelType::LgbmClassifier,
    ModelType::LgbmRegressor,
    ModelType::XgbRegressor,
];

pub const AVAILABLE_MODEL_TYPES: &[ModelType] = &[
    ModelType::Transformers,
    ModelType::SklearnPipeline,
    ModelType::SklearnEstimator,
    ModelType::StackingRegressor,
    ModelType::StackingClassifier,
    ModelType::StackingEstimator,
    ModelType::CalibratedClassifier,
    ModelType::LgbmRegressor,
    ModelType::LgbmClassifier,
    ModelType::XgbRegressor,
    ModelType::XgbClassifier,
    ModelType::XgbBooster,
    ModelType::LgbmBooster,
    ModelType::TfKeras,
    ModelType::Pytorch,
    ModelType::PytorchLightning,
    ModelType::Catboost,
    ModelType::Vowpal,
];
