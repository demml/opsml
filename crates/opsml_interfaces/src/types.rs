use crate::error::TypeError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pythonize::pythonize;
use serde::de::MapAccess;
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

    pub fn __getitem__(&self, key: &str) -> Result<Feature, TypeError> {
        match self.items.get(key) {
            Some(value) => Ok(value.clone()),
            None => Err(TypeError::MissingKeyError(key.to_string())),
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

/// Deserialize a dictionary field that may be null into Option<Py<PyDict>>
pub(crate) fn deserialize_dict_field<'de, A>(
    map: &mut A,
    py: Python<'_>,
) -> Result<Option<Py<PyDict>>, A::Error>
where
    A: MapAccess<'de>,
{
    let value = map.next_value::<serde_json::Value>()?;
    match value {
        serde_json::Value::Null => Ok(None),
        _ => {
            let py_obj = pythonize(py, &value)
                .map_err(|e| serde::de::Error::custom(format!("Deserialization failed: {}", e)))?;

            let dict = py_obj
                .cast::<PyDict>()
                .map_err(|_| serde::de::Error::custom("Expected a dictionary"))?
                .clone();

            Ok(Some(dict.unbind()))
        }
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
