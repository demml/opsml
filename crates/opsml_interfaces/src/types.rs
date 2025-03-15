use opsml_error::OpsmlError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::fmt::Display;

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

    #[pyo3(get, set)]
    pub onnx_type: String,
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
            onnx_type: "onnx".to_string(),
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

// add matching function that compares string to ModelType

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceModuleType {
    PretrainedModel,
    TransformerModel,
    TransformerPipeline,
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub enum ProcessorType {
    Preprocessor,
    Tokenizer,
    FeatureExtractor,
    ImageProcessor,
}

impl Display for ProcessorType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ProcessorType::Preprocessor => write!(f, "preprocessor"),
            ProcessorType::Tokenizer => write!(f, "tokenizer"),
            ProcessorType::FeatureExtractor => write!(f, "feature_extractor"),
            ProcessorType::ImageProcessor => write!(f, "image_processor"),
        }
    }
}
