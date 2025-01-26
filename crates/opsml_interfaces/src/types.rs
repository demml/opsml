use opsml_error::OpsmlError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::fmt::Display;
use std::fmt::Formatter;
use tracing::debug;

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct Feature {
    #[pyo3(get, set)]
    pub feature_type: String,
    #[pyo3(get, set)]
    pub shape: Vec<i64>,
    #[pyo3(get, set)]
    extra_args: HashMap<String, String>,
}

#[pymethods]
impl Feature {
    #[new]
    #[pyo3(signature = (feature_type, shape, extra_args=None))]
    pub fn new(
        feature_type: String,
        shape: Vec<i64>,
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

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct OnnxSchema {
    #[pyo3(get, set)]
    pub input_features: FeatureSchema,

    #[pyo3(get, set)]
    pub output_features: FeatureSchema,

    #[pyo3(get, set)]
    pub onnx_version: String,

    #[pyo3(get)]
    pub feature_names: Vec<String>,
}

#[pymethods]
impl OnnxSchema {
    #[new]
    #[pyo3(signature = (input_features, output_features, onnx_version, feature_names=None))]
    fn new(
        input_features: FeatureSchema,
        output_features: FeatureSchema,
        onnx_version: String,
        feature_names: Option<Vec<String>>,
    ) -> Self {
        OnnxSchema {
            input_features,
            output_features,
            onnx_version,
            feature_names: feature_names.unwrap_or_default(),
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
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

#[pyclass(eq, eq_int)]
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
    TensorFlow,
    TfKeras,
    Pytorch,
    PytorchLightning,
    Catboost,
    Vowpal,
    Unknown,
}

impl Display for ModelType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        // match the types and return the string representation
        let model_type = match self {
            ModelType::Transformers => "transformers",
            ModelType::SklearnPipeline => "Pipeline",
            ModelType::SklearnEstimator => "SklearnEstimator",
            ModelType::StackingRegressor => "StackingRegressor",
            ModelType::StackingClassifier => "StackingClassifier",
            ModelType::StackingEstimator => "StackingEstimator",
            ModelType::CalibratedClassifier => "CalibratedClassifierCV",
            ModelType::LgbmRegressor => "LGBMRegressor",
            ModelType::LgbmClassifier => "LGBMClassifier",
            ModelType::XgbRegressor => "XGBRegressor",
            ModelType::XgbClassifier => "XGBClassifier",
            ModelType::XgbBooster => "Booster",
            ModelType::LgbmBooster => "Booster",
            ModelType::TensorFlow => "TensorFlow",
            ModelType::TfKeras => "keras",
            ModelType::Pytorch => "pytorch",
            ModelType::PytorchLightning => "pytorch_lightning",
            ModelType::Catboost => "CatBoost",
            ModelType::Vowpal => "VowpalWabbit",
            ModelType::Unknown => "Unknown",
        };

        write!(f, "{}", model_type)
    }
}

impl ModelType {
    pub fn get_type(model_type: &str, module: &str) -> ModelType {
        match model_type {
            "transformers" => ModelType::Transformers,
            "Pipeline" => ModelType::SklearnPipeline,
            "SklearnEstimator" => ModelType::SklearnEstimator,
            "StackingRegressor" => ModelType::StackingRegressor,
            "StackingClassifier" => ModelType::StackingClassifier,
            "StackingEstimator" => ModelType::StackingEstimator,
            "CalibratedClassifierCV" => ModelType::CalibratedClassifier,
            "LGBMRegressor" => ModelType::LgbmRegressor,
            "LGBMClassifier" => ModelType::LgbmClassifier,
            "XGBRegressor" => ModelType::XgbRegressor,
            "XGBClassifier" => ModelType::XgbClassifier,
            "Booster" => {
                if module.contains("lightgbm") {
                    ModelType::LgbmBooster
                } else {
                    ModelType::XgbBooster
                }
            }
            "tensorflow" => ModelType::TensorFlow,
            "keras" => ModelType::TfKeras,
            "pytorch" => ModelType::Pytorch,
            "pytorch_lightning" => ModelType::PytorchLightning,
            "CatBoost" => ModelType::Catboost,
            "VowpalWabbit" => ModelType::Vowpal,
            _ => ModelType::Unknown,
        }
    }

    pub fn from_pyobject(object: &Bound<'_, PyAny>) -> ModelType {
        let model_type = object
            .getattr("__class__")
            .unwrap()
            .getattr("__name__")
            .unwrap()
            .extract::<String>()
            .unwrap();

        let module = object
            .getattr("__class__")
            .unwrap()
            .getattr("__module__")
            .unwrap()
            .extract::<String>()
            .unwrap();

        debug!("ModelType: {}, Module type: {}", model_type, module);

        ModelType::get_type(&model_type, &module)
    }

    pub fn in_update_registry(&self) -> bool {
        UPDATE_REGISTRY_MODELS.contains(self)
    }

    pub fn in_sklearn_registry(&self) -> bool {
        SKLEARN_SUPPORTED_MODEL_TYPES.contains(self)
    }

    pub fn get_onnx_update_type(&self) -> ModelType {
        match self {
            ModelType::StackingRegressor => ModelType::StackingEstimator,
            ModelType::StackingClassifier => ModelType::StackingEstimator,
            ModelType::StackingEstimator => ModelType::StackingEstimator,
            _ => self.clone(),
        }
    }
}

// add matching function that compares string to ModelType

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
    ModelType::XgbClassifier,
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
