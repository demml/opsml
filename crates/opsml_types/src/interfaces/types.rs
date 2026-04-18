use crate::DataType;
use scouter_client::DriftType;
use serde::{Deserialize, Deserializer, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::fmt::Display;
use std::fmt::Formatter;
use std::path::PathBuf;

#[cfg(feature = "python")]
use {
    crate::{
        CommonKwargs,
        error::{OnnxError, TypeError},
    },
    opsml_utils::{PyHelperFuncs, deserialize_dict_field},
    pyo3::{
        IntoPyObjectExt, PyTraverseError, PyVisit,
        prelude::*,
        types::{PyDict, PyList, PyType},
    },
    pythonize::depythonize,
    serde::{
        de::{self, MapAccess, Visitor},
        ser::{SerializeStruct, Serializer},
    },
    serde_json::{Value, json},
    std::path::Path,
    tracing::{debug, error, instrument},
};

#[cfg(all(
    feature = "python",
    not(all(target_arch = "x86_64", target_os = "macos"))
))]
use ort::{session::Session, value::ValueType};
#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub enum TaskType {
    Classification,
    Regression,
    Clustering,
    AnomalyDetection,
    TimeSeries,
    Forecasting,
    Recommendation,
    Ranking,
    Nlp,
    Image,
    Audio,
    Video,
    Graph,
    Tabular,
    TimeSeriesForecasting,
    TimeSeriesAnomalyDetection,
    TimeSeriesClassification,
    TimeSeriesRegression,
    TimeSeriesClustering,
    TimeSeriesRecommendation,
    TimeSeriesRanking,
    TimeSeriesNLP,
    TimeSeriesImage,
    TimeSeriesAudio,
    TimeSeriesVideo,
    TimeSeriesGraph,
    TimeSeriesTabular,
    Optimization,
    #[default]
    Undefined,
}

impl Display for TaskType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        let task_type = match self {
            TaskType::Classification => "Classification",
            TaskType::Regression => "Regression",
            TaskType::Clustering => "Clustering",
            TaskType::AnomalyDetection => "AnomalyDetection",
            TaskType::TimeSeries => "TimeSeries",
            TaskType::Forecasting => "Forecasting",
            TaskType::Recommendation => "Recommendation",
            TaskType::Ranking => "Ranking",
            TaskType::Nlp => "Nlp",
            TaskType::Image => "Image",
            TaskType::Audio => "Audio",
            TaskType::Video => "Video",
            TaskType::Graph => "Graph",
            TaskType::Tabular => "Tabular",
            TaskType::TimeSeriesForecasting => "TimeSeriesForecasting",
            TaskType::TimeSeriesAnomalyDetection => "TimeSeriesAnomalyDetection",
            TaskType::TimeSeriesClassification => "TimeSeriesClassification",
            TaskType::TimeSeriesRegression => "TimeSeriesRegression",
            TaskType::TimeSeriesClustering => "TimeSeriesClustering",
            TaskType::TimeSeriesRecommendation => "TimeSeriesRecommendation",
            TaskType::TimeSeriesRanking => "TimeSeriesRanking",
            TaskType::TimeSeriesNLP => "TimeSeriesNLP",
            TaskType::TimeSeriesImage => "TimeSeriesImage",
            TaskType::TimeSeriesAudio => "TimeSeriesAudio",
            TaskType::TimeSeriesVideo => "TimeSeriesVideo",
            TaskType::TimeSeriesGraph => "TimeSeriesGraph",
            TaskType::TimeSeriesTabular => "TimeSeriesTabular",
            TaskType::Optimization => "Optimization",
            TaskType::Undefined => "Undefined",
        };

        write!(f, "{task_type}")
    }
}

#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
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
    Onnx,
}

impl Display for ModelInterfaceType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        let model_interface_type = match self {
            ModelInterfaceType::Base => "Base",
            ModelInterfaceType::Sklearn => "Sklearn",
            ModelInterfaceType::CatBoost => "CatBoost",
            ModelInterfaceType::HuggingFace => "HuggingFace",
            ModelInterfaceType::LightGBM => "LightGBM",
            ModelInterfaceType::Lightning => "Lightning",
            ModelInterfaceType::Torch => "Torch",
            ModelInterfaceType::TensorFlow => "TensorFlow",
            ModelInterfaceType::VowpalWabbit => "VowpalWabbit",
            ModelInterfaceType::XGBoost => "XGBoost",
            ModelInterfaceType::Onnx => "Onnx",
        };

        write!(f, "{model_interface_type}")
    }
}

#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum DataInterfaceType {
    #[default]
    Base,
    Arrow,
    Numpy,
    Pandas,
    Polars,
    Sql,
    Torch,
}

impl Display for DataInterfaceType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        let data_interface_type = match self {
            DataInterfaceType::Base => "Base",
            DataInterfaceType::Arrow => "Arrow",
            DataInterfaceType::Numpy => "Numpy",
            DataInterfaceType::Pandas => "Pandas",
            DataInterfaceType::Polars => "Polars",
            DataInterfaceType::Sql => "Sql",
            DataInterfaceType::Torch => "Torch",
        };

        write!(f, "{data_interface_type}")
    }
}

#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
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
    Onnx,

    #[default]
    Unknown,
}

impl Display for ModelType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
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
            ModelType::Onnx => "onnx",
        };

        write!(f, "{model_type}")
    }
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
            "CatBoostRegressor" => ModelType::Catboost,
            "CatBoostClassifier" => ModelType::Catboost,
            "CatBoostRanker" => ModelType::Catboost,
            "VowpalWabbit" => ModelType::Vowpal,
            _ => ModelType::Unknown,
        }
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

#[cfg(feature = "python")]
impl ModelType {
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
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DriftProfileUri {
    pub root_dir: PathBuf,
    pub uri: PathBuf,
    pub drift_type: DriftType,
}

#[cfg(feature = "python")]
#[pymethods]
impl DriftProfileUri {
    #[getter]
    pub fn root_dir(&self) -> PathBuf {
        self.root_dir.clone()
    }
    #[getter]
    pub fn uri(&self) -> PathBuf {
        self.uri.clone()
    }
    #[getter]
    pub fn drift_type(&self) -> DriftType {
        self.drift_type.clone()
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Default, Clone, Deserialize, Serialize, PartialEq)]
pub struct DriftArgs {
    pub active: bool,
    pub deactivate_others: bool,
}

#[cfg(feature = "python")]
#[pymethods]
impl DriftArgs {
    #[new]
    #[pyo3(signature = (active=true, deactivate_others=false))]
    pub fn new(active: bool, deactivate_others: bool) -> Self {
        Self {
            active,
            deactivate_others,
        }
    }

    #[getter]
    pub fn active(&self) -> bool {
        self.active
    }

    #[getter]
    pub fn deactivate_others(&self) -> bool {
        self.deactivate_others
    }

    #[setter]
    pub fn set_active(&mut self, active: bool) {
        self.active = active;
    }

    #[setter]
    pub fn set_deactivate_others(&mut self, deactivate_others: bool) {
        self.deactivate_others = deactivate_others;
    }
}

// ---------------------------------------------------------------------------
// Feature schema types
// ---------------------------------------------------------------------------

#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct Feature {
    pub feature_type: String,
    pub shape: Vec<i64>,
    pub extra_args: HashMap<String, String>,
}

#[cfg(feature = "python")]
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

    #[getter]
    pub fn feature_type(&self) -> &str {
        &self.feature_type
    }

    #[setter]
    pub fn set_feature_type(&mut self, val: String) {
        self.feature_type = val;
    }

    #[getter]
    pub fn shape(&self) -> Vec<i64> {
        self.shape.clone()
    }

    #[setter]
    pub fn set_shape(&mut self, val: Vec<i64>) {
        self.shape = val;
    }

    #[getter]
    pub fn extra_args(&self) -> HashMap<String, String> {
        self.extra_args.clone()
    }

    #[setter]
    pub fn set_extra_args(&mut self, val: HashMap<String, String>) {
        self.extra_args = val;
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct FeatureSchema {
    pub items: HashMap<String, Feature>,
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

#[cfg(feature = "python")]
#[pymethods]
impl FeatureSchema {
    #[new]
    #[pyo3(signature = (items=None))]
    pub fn new(items: Option<HashMap<String, Feature>>) -> Self {
        FeatureSchema {
            items: items.unwrap_or_default(),
        }
    }

    #[getter]
    pub fn items(&self) -> HashMap<String, Feature> {
        self.items.clone()
    }

    #[setter]
    pub fn set_items(&mut self, val: HashMap<String, Feature>) {
        self.items = val;
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn __getitem__(&self, key: &str) -> PyResult<Feature> {
        self.items
            .get(key)
            .cloned()
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(format!("Key not found: {key}")))
    }
}

#[cfg(feature = "python")]
#[pyclass(from_py_object)]
#[derive(Debug)]
pub struct ExtraMetadata {
    metadata: Py<PyDict>,
}

#[cfg(feature = "python")]
#[pymethods]
impl ExtraMetadata {
    #[new]
    #[pyo3(signature = (metadata))]
    pub fn new(metadata: Bound<'_, PyDict>) -> Self {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let metadata = metadata.unbind();
        Self { metadata }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__json__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[cfg(feature = "python")]
impl Serialize for ExtraMetadata {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::attach(|py| {
            let mut state = serializer.serialize_struct("ExtraMetadata", 1)?;
            let metadata: serde_json::Value = depythonize(self.metadata.bind(py)).map_err(|e| {
                serde::ser::Error::custom(format!("Failed to serialize metadata: {}", e))
            })?;

            state.serialize_field("metadata", &metadata)?;
            state.end()
        })
    }
}

#[cfg(feature = "python")]
impl<'de> Deserialize<'de> for ExtraMetadata {
    fn deserialize<D>(deserializer: D) -> Result<ExtraMetadata, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct ExtraMetadataVisitor;

        impl<'de> serde::de::Visitor<'de> for ExtraMetadataVisitor {
            type Value = ExtraMetadata;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ExtraMetadata")
            }

            fn visit_map<A>(self, mut map: A) -> Result<ExtraMetadata, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::attach(|py| {
                    let mut metadata = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "metadata" => {
                                metadata = deserialize_dict_field(&mut map, py)?;
                            }

                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }
                    let kwargs = ExtraMetadata {
                        metadata: metadata.unwrap(),
                    };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct("ExtraMetadata", &["metadata"], ExtraMetadataVisitor)
    }
}

#[cfg(feature = "python")]
impl Clone for ExtraMetadata {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let metadata = self.metadata.clone_ref(py);

            ExtraMetadata { metadata }
        })
    }
}

#[cfg(feature = "python")]
#[pyclass(eq, eq_int, from_py_object)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceORTModel {
    OrtAudioClassification,
    OrtAudioFrameClassification,
    OrtAudioXVector,
    OrtCustomTasks,
    OrtCtc,
    OrtFeatureExtraction,
    OrtImageClassification,
    OrtMaskedLm,
    OrtMultipleChoice,
    OrtQuestionAnswering,
    OrtSemanticSegmentation,
    OrtSequenceClassification,
    OrtTokenClassification,
    OrtSeq2SeqLm,
    OrtSpeechSeq2Seq,
    OrtVision2Seq,
    OrtPix2Struct,
    OrtCausalLm,
    OrtOptimizer,
    OrtQuantizer,
    OrtTrainer,
    OrtSeq2SeqTrainer,
    OrtTrainingArguments,
    OrtSeq2SeqTrainingArguments,
    OrtStableDiffusionPipeline,
    OrtStableDiffusionImg2ImgPipeline,
    OrtStableDiffusionInpaintPipeline,
    OrtStableDiffusionXlPipeline,
    OrtStableDiffusionXlImg2ImgPipeline,
}

#[cfg(feature = "python")]
impl Display for HuggingFaceORTModel {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            HuggingFaceORTModel::OrtAudioClassification => {
                write!(f, "ORTModelForAudioClassification")
            }
            HuggingFaceORTModel::OrtAudioFrameClassification => {
                write!(f, "ORTModelForAudioFrameClassification")
            }
            HuggingFaceORTModel::OrtAudioXVector => write!(f, "ORTModelForAudioXVector"),
            HuggingFaceORTModel::OrtCustomTasks => write!(f, "ORTModelForCustomTasks"),
            HuggingFaceORTModel::OrtCtc => write!(f, "ORTModelForCTC"),
            HuggingFaceORTModel::OrtFeatureExtraction => write!(f, "ORTModelForFeatureExtraction"),
            HuggingFaceORTModel::OrtImageClassification => {
                write!(f, "ORTModelForImageClassification")
            }
            HuggingFaceORTModel::OrtMaskedLm => write!(f, "ORTModelForMaskedLM"),
            HuggingFaceORTModel::OrtMultipleChoice => write!(f, "ORTModelForMultipleChoice"),
            HuggingFaceORTModel::OrtQuestionAnswering => write!(f, "ORTModelForQuestionAnswering"),
            HuggingFaceORTModel::OrtSemanticSegmentation => {
                write!(f, "ORTModelForSemanticSegmentation")
            }
            HuggingFaceORTModel::OrtSequenceClassification => {
                write!(f, "ORTModelForSequenceClassification")
            }
            HuggingFaceORTModel::OrtTokenClassification => {
                write!(f, "ORTModelForTokenClassification")
            }
            HuggingFaceORTModel::OrtSeq2SeqLm => write!(f, "ORTModelForSeq2SeqLM"),
            HuggingFaceORTModel::OrtSpeechSeq2Seq => write!(f, "ORTModelForSpeechSeq2Seq"),
            HuggingFaceORTModel::OrtVision2Seq => write!(f, "ORTModelForVision2Seq"),
            HuggingFaceORTModel::OrtPix2Struct => write!(f, "ORTModelForPix2Struct"),
            HuggingFaceORTModel::OrtCausalLm => write!(f, "ORTModelForCausalLM"),
            HuggingFaceORTModel::OrtOptimizer => write!(f, "ORTOptimizer"),
            HuggingFaceORTModel::OrtQuantizer => write!(f, "ORTQuantizer"),
            HuggingFaceORTModel::OrtTrainer => write!(f, "ORTTrainer"),
            HuggingFaceORTModel::OrtSeq2SeqTrainer => write!(f, "ORTSeq2SeqTrainer"),
            HuggingFaceORTModel::OrtTrainingArguments => write!(f, "ORTTrainingArguments"),
            HuggingFaceORTModel::OrtSeq2SeqTrainingArguments => {
                write!(f, "ORTSeq2SeqTrainingArguments")
            }
            HuggingFaceORTModel::OrtStableDiffusionPipeline => {
                write!(f, "ORTStableDiffusionPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionImg2ImgPipeline => {
                write!(f, "ORTStableDiffusionImg2ImgPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionInpaintPipeline => {
                write!(f, "ORTStableDiffusionInpaintPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionXlPipeline => {
                write!(f, "ORTStableDiffusionXLPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionXlImg2ImgPipeline => {
                write!(f, "ORTStableDiffusionXLImg2ImgPipeline")
            }
        }
    }
}

#[cfg(feature = "python")]
#[pyclass(skip_from_py_object)]
#[derive(Debug)]
pub struct HuggingFaceOnnxArgs {
    #[pyo3(get)]
    pub ort_type: HuggingFaceORTModel,

    #[pyo3(get)]
    pub provider: String,

    #[pyo3(get)]
    pub quantize: bool,

    #[pyo3(get)]
    pub config: Option<Py<PyAny>>,

    #[pyo3(get)]
    pub extra_kwargs: Py<PyDict>,
}

#[cfg(feature = "python")]
#[pymethods]
impl HuggingFaceOnnxArgs {
    #[new]
    #[pyo3(signature = (ort_type, provider=None, quantize=false, config=None, extra_kwargs=None))]
    pub fn new(
        py: Python,
        ort_type: HuggingFaceORTModel,
        provider: Option<String>,
        quantize: Option<bool>,
        config: Option<&Bound<'_, PyAny>>,
        extra_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Self, TypeError> {
        // check if ort_type is valid (does it match any of the HuggingFaceORTModel enum variants?)

        let config = HuggingFaceOnnxArgs::check_optimum_config(py, config)?;
        let extra_kwargs = extra_kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());

        Ok(HuggingFaceOnnxArgs {
            ort_type,
            provider: provider.unwrap_or_else(|| "CPUExecutionProvider".to_string()),
            quantize: quantize.unwrap_or(false),
            config,
            extra_kwargs: extra_kwargs.unbind(),
        })
    }

    pub fn to_dict<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyDict>, TypeError> {
        let dict = PyDict::new(py);
        dict.set_item("ort_type", self.ort_type.to_string().clone())?;
        dict.set_item("provider", self.provider.clone())?;
        dict.set_item("quantize", self.quantize)?;
        dict.set_item("config", self.config.as_ref())?;
        dict.set_item("extra_kwargs", self.extra_kwargs.bind(py).clone())?;

        Ok(dict)
    }
}

#[cfg(feature = "python")]
impl HuggingFaceOnnxArgs {
    fn check_optimum_config(
        py: Python,
        config: Option<&Bound<'_, PyAny>>,
    ) -> Result<Option<Py<PyAny>>, TypeError> {
        if config.is_none() {
            return Ok(None);
        }

        let config = config.unwrap();

        // Import the necessary classes from the optimum.onnxruntime module
        let optimum_module = py.import("optimum.onnxruntime")?;
        let auto_quantization_config_attr = optimum_module.getattr("AutoQuantizationConfig")?;
        let auto_quantization_config = auto_quantization_config_attr.cast::<PyType>()?;

        let ort_config_attr = optimum_module.getattr("ORTConfig")?;
        let ort_config = ort_config_attr.cast::<PyType>()?;

        let quantization_config_attr = optimum_module.getattr("QuantizationConfig")?;
        let quantization_config = quantization_config_attr.cast::<PyType>()?;

        // Assert that config is an instance of one of the specified classes
        let is_valid_config = config.is_instance(auto_quantization_config)?
            || config.is_instance(ort_config)?
            || config.is_instance(quantization_config)?;

        if !is_valid_config {
            return Err(TypeError::HuggingFaceOnnxArgTypeError);
        }

        Ok(Some(config.into_py_any(py)?))
    }
}

#[cfg(feature = "python")]
#[pyclass(from_py_object)]
#[derive(Debug, Default)]
pub struct ModelSaveKwargs {
    pub onnx: Option<Py<PyDict>>,

    pub model: Option<Py<PyDict>>,

    pub preprocessor: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub save_onnx: bool,

    #[pyo3(get, set)]
    pub drift: Option<DriftArgs>,
}

#[cfg(feature = "python")]
#[pymethods]
impl ModelSaveKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None, save_onnx=None, drift=None))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
        save_onnx: Option<bool>,
        drift: Option<DriftArgs>,
    ) -> Result<Self, TypeError> {
        let mut save_onnx = save_onnx.unwrap_or(false);
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.cast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.cast::<PyDict>().unwrap().clone().unbind())
            } else {
                Err(TypeError::InvalidOnnxType)
            }
        });

        // set save_onnx to true if onnx is not None
        let onnx = match onnx {
            Some(Ok(onnx)) => {
                save_onnx = true;
                Some(onnx)
            }
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
            save_onnx,
            drift,
        })
    }

    pub fn __str__(&self, py: Python) -> String {
        let mut onnx = Value::Null;
        let mut model = Value::Null;
        let mut preprocessor = Value::Null;

        if let Some(onnx_args) = &self.onnx {
            onnx = depythonize(onnx_args.bind(py)).unwrap();
        }

        if let Some(model_args) = &self.model {
            model = depythonize(model_args.bind(py)).unwrap();
        }

        if let Some(preprocessor_args) = &self.preprocessor {
            preprocessor = depythonize(preprocessor_args.bind(py)).unwrap();
        }

        let json = json!({
            "onnx": onnx,
            "model": model,
            "preprocessor": preprocessor,
        });

        PyHelperFuncs::__str__(json)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[cfg(feature = "python")]
impl ModelSaveKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().map(|onnx| onnx.bind(py))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.model.as_ref().map(|model| model.bind(py))
    }

    pub fn preprocessor_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<Py<PyAny>> into Option<Bound<_, PyDict>>
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.bind(py))
    }

    pub fn save_onnx(&self) -> bool {
        self.save_onnx
    }
}

#[cfg(feature = "python")]
impl Serialize for ModelSaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::attach(|py| {
            let mut state = serializer.serialize_struct("ModelSaveKwargs", 5)?;

            let onnx: Option<serde_json::Value> = self
                .onnx
                .as_ref()
                .map(|onnx| depythonize(onnx.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize onnx: {}", e))
                })?;

            let model: Option<serde_json::Value> = self
                .model
                .as_ref()
                .map(|model| depythonize(model.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize model: {}", e))
                })?;

            let preprocessor: Option<serde_json::Value> = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| depythonize(preprocessor.bind(py)))
                .transpose()
                .map_err(|e| {
                    serde::ser::Error::custom(format!("Failed to serialize preprocessor: {}", e))
                })?;

            state.serialize_field("onnx", &onnx)?;
            state.serialize_field("model", &model)?;
            state.serialize_field("preprocessor", &preprocessor)?;
            state.serialize_field("save_onnx", &self.save_onnx)?;
            state.serialize_field("drift", &self.drift)?;
            state.end()
        })
    }
}

#[cfg(feature = "python")]
impl<'de> Deserialize<'de> for ModelSaveKwargs {
    fn deserialize<D>(deserializer: D) -> Result<ModelSaveKwargs, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct ModelSaveKwargsVisitor;

        impl<'de> serde::de::Visitor<'de> for ModelSaveKwargsVisitor {
            type Value = ModelSaveKwargs;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ModelSaveKwargs")
            }

            fn visit_map<A>(self, mut map: A) -> Result<ModelSaveKwargs, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::attach(|py| {
                    let mut onnx = None;
                    let mut model = None;
                    let mut preprocessor = None;
                    let mut save_onnx = None;
                    let mut drift = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "onnx" => {
                                onnx = deserialize_dict_field(&mut map, py)?;
                            }
                            "model" => {
                                model = deserialize_dict_field(&mut map, py)?;
                            }
                            "preprocessor" => {
                                preprocessor = deserialize_dict_field(&mut map, py)?;
                            }
                            "save_onnx" => {
                                save_onnx = map.next_value::<Option<bool>>()?;
                            }
                            "drift" => {
                                drift = map.next_value::<Option<DriftArgs>>()?;
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }

                    let kwargs = ModelSaveKwargs {
                        onnx,
                        model,
                        preprocessor,
                        save_onnx: save_onnx.unwrap_or(false),
                        drift,
                    };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct(
            "ModelSaveKwargs",
            &["onnx", "model", "preprocessor", "save_onnx"],
            ModelSaveKwargsVisitor,
        )
    }
}

#[cfg(feature = "python")]
impl Clone for ModelSaveKwargs {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));
            let save_onnx = self.save_onnx;
            let drift = self.drift.clone();

            ModelSaveKwargs {
                onnx,
                model,
                preprocessor,
                save_onnx,
                drift,
            }
        })
    }
}
#[cfg_attr(feature = "python", pyclass(eq, from_py_object))]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub enum ProcessorType {
    Preprocessor,
    Tokenizer,
    FeatureExtractor,
    ImageProcessor,
}

impl Display for ProcessorType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        match self {
            ProcessorType::Preprocessor => write!(f, "preprocessor"),
            ProcessorType::Tokenizer => write!(f, "tokenizer"),
            ProcessorType::FeatureExtractor => write!(f, "feature_extractor"),
            ProcessorType::ImageProcessor => write!(f, "image_processor"),
        }
    }
}

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataProcessor {
    pub name: String,
    pub uri: PathBuf,
    pub r#type: ProcessorType,
}

#[cfg(feature = "python")]
#[pymethods]
impl DataProcessor {
    #[new]
    pub fn new(name: String, uri: PathBuf, r#type: ProcessorType) -> Self {
        DataProcessor { name, uri, r#type }
    }

    #[getter]
    pub fn name(&self) -> &str {
        &self.name
    }

    #[getter]
    pub fn uri(&self) -> PathBuf {
        self.uri.clone()
    }

    #[getter]
    pub fn r#type(&self) -> ProcessorType {
        self.r#type.clone()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

// ---------------------------------------------------------------------------
// Model interface metadata types
// ---------------------------------------------------------------------------

/// Metadata produced during model interface save. Python-bound fields
/// (`extra`, `save_kwargs`) are stored as opaque JSON values so that the
/// struct is fully serialisable in a pure-Rust context (e.g. the CLI).
#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelInterfaceSaveMetadata {
    pub model_uri: PathBuf,
    pub data_processor_map: HashMap<String, DataProcessor>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sample_data_uri: Option<PathBuf>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub onnx_model_uri: Option<PathBuf>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub drift_profile_uri_map: Option<HashMap<String, DriftProfileUri>>,

    /// Serialised `ExtraMetadata` — only present in Python builds.
    #[cfg(feature = "python")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra: Option<ExtraMetadata>,

    /// Serialised `ModelSaveKwargs` — only present in Python builds.
    #[cfg(feature = "python")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub save_kwargs: Option<ModelSaveKwargs>,
}

#[cfg(feature = "python")]
#[pymethods]
impl ModelInterfaceSaveMetadata {
    #[new]
    #[pyo3(signature = (model_uri, data_processor_map=None, sample_data_uri=None, onnx_model_uri=None, drift_profile_uri_map=None, extra=None, save_kwargs=None))]
    pub fn new(
        model_uri: PathBuf,
        data_processor_map: Option<HashMap<String, DataProcessor>>,
        sample_data_uri: Option<PathBuf>,
        onnx_model_uri: Option<PathBuf>,
        drift_profile_uri_map: Option<HashMap<String, DriftProfileUri>>,
        extra: Option<ExtraMetadata>,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Self {
        ModelInterfaceSaveMetadata {
            model_uri,
            data_processor_map: data_processor_map.unwrap_or_default(),
            sample_data_uri,
            onnx_model_uri,
            drift_profile_uri_map,
            extra,
            save_kwargs,
        }
    }

    #[getter]
    pub fn model_uri(&self) -> PathBuf {
        self.model_uri.clone()
    }

    #[setter]
    pub fn set_model_uri(&mut self, val: PathBuf) {
        self.model_uri = val;
    }

    #[getter]
    pub fn data_processor_map(&self) -> HashMap<String, DataProcessor> {
        self.data_processor_map.clone()
    }

    #[getter]
    pub fn sample_data_uri(&self) -> Option<PathBuf> {
        self.sample_data_uri.clone()
    }

    #[getter]
    pub fn onnx_model_uri(&self) -> Option<PathBuf> {
        self.onnx_model_uri.clone()
    }

    #[getter]
    pub fn drift_profile_uri_map(&self) -> Option<HashMap<String, DriftProfileUri>> {
        self.drift_profile_uri_map.clone()
    }

    #[getter]
    pub fn extra(&self) -> Option<ExtraMetadata> {
        self.extra.clone()
    }

    #[getter]
    pub fn save_kwargs(&self) -> Option<ModelSaveKwargs> {
        self.save_kwargs.clone()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        PyHelperFuncs::__json__(self)
    }
}

/// Full model interface metadata. The `onnx_session` field is an opaque JSON
/// value (serialised `OnnxSession`) so the struct is usable without Python.
#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelInterfaceMetadata {
    pub task_type: TaskType,
    pub model_type: ModelType,
    pub data_type: DataType,

    /// Serialised `OnnxSession` — only present in Python builds.
    #[cfg(feature = "python")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub onnx_session: Option<OnnxSession>,

    pub schema: FeatureSchema,
    pub save_metadata: ModelInterfaceSaveMetadata,
    pub extra_metadata: HashMap<String, String>,
    pub interface_type: ModelInterfaceType,
    pub model_specific_metadata: serde_json::Value,
    pub version: String,
}

#[cfg(feature = "python")]
#[pymethods]
impl ModelInterfaceMetadata {
    #[new]
    #[pyo3(signature = (
        save_metadata,
        task_type=TaskType::Undefined,
        model_type=ModelType::Unknown,
        data_type=DataType::NotProvided,
        schema=FeatureSchema::default(),
        interface_type=ModelInterfaceType::Base,
        onnx_session=None,
        extra_metadata=HashMap::new(),
        version=CommonKwargs::Undefined.to_string()
     )
    )]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        save_metadata: ModelInterfaceSaveMetadata,
        task_type: TaskType,
        model_type: ModelType,
        data_type: DataType,
        schema: FeatureSchema,
        interface_type: ModelInterfaceType,
        onnx_session: Option<OnnxSession>,
        extra_metadata: HashMap<String, String>,
        version: String,
    ) -> Self {
        ModelInterfaceMetadata {
            task_type,
            model_type,
            data_type,
            onnx_session,
            schema,
            interface_type,
            save_metadata,
            extra_metadata,
            model_specific_metadata: Value::Null,
            version,
        }
    }

    #[getter]
    pub fn task_type(&self) -> TaskType {
        self.task_type.clone()
    }

    #[setter]
    pub fn set_task_type(&mut self, val: TaskType) {
        self.task_type = val;
    }

    #[getter]
    pub fn model_type(&self) -> ModelType {
        self.model_type.clone()
    }

    #[setter]
    pub fn set_model_type(&mut self, val: ModelType) {
        self.model_type = val;
    }

    #[getter]
    pub fn data_type(&self) -> DataType {
        self.data_type.clone()
    }

    #[setter]
    pub fn set_data_type(&mut self, val: DataType) {
        self.data_type = val;
    }

    #[getter]
    pub fn onnx_session(&self) -> Option<OnnxSession> {
        self.onnx_session.clone()
    }

    #[getter]
    pub fn schema(&self) -> FeatureSchema {
        self.schema.clone()
    }

    #[setter]
    pub fn set_schema(&mut self, val: FeatureSchema) {
        self.schema = val;
    }

    #[getter]
    pub fn save_metadata(&self) -> ModelInterfaceSaveMetadata {
        self.save_metadata.clone()
    }

    #[getter]
    pub fn extra_metadata(&self) -> HashMap<String, String> {
        self.extra_metadata.clone()
    }

    #[setter]
    pub fn set_extra_metadata(&mut self, val: HashMap<String, String>) {
        self.extra_metadata = val;
    }

    #[getter]
    pub fn interface_type(&self) -> ModelInterfaceType {
        self.interface_type.clone()
    }

    #[setter]
    pub fn set_interface_type(&mut self, val: ModelInterfaceType) {
        self.interface_type = val;
    }

    #[getter]
    pub fn version(&self) -> String {
        self.version.clone()
    }

    #[setter]
    pub fn set_version(&mut self, val: String) {
        self.version = val;
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> ModelInterfaceMetadata {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[cfg(all(
    feature = "python",
    not(all(target_arch = "x86_64", target_os = "macos"))
))]
fn parse_session_schema(
    ort_session: &Session,
) -> Result<(FeatureSchema, FeatureSchema), OnnxError> {
    let input_schema = ort_session
        .inputs()
        .iter()
        .map(|input| {
            let name = input.name().to_string();
            let input_type = input.dtype().clone();

            let feature = match input_type {
                ValueType::Tensor {
                    ty,
                    shape,
                    dimension_symbols: _,
                } => Feature::new(ty.to_string(), shape.to_vec(), None),
                _ => Feature::new("Unknown".to_string(), vec![], None),
            };

            Ok((name, feature))
        })
        .collect::<Result<FeatureSchema, OnnxError>>()?;

    let output_schema = ort_session
        .outputs()
        .iter()
        .map(|output| {
            let name = output.name().to_string();
            let input_type = output.dtype().clone();
            let feature = match input_type {
                ValueType::Tensor {
                    ty,
                    shape,
                    dimension_symbols: _,
                } => Feature::new(ty.to_string(), shape.to_vec(), None),
                _ => Feature::new("Unknown".to_string(), vec![], None),
            };

            Ok((name, feature))
        })
        .collect::<Result<FeatureSchema, OnnxError>>()?;

    Ok((input_schema, output_schema))
}

#[cfg(feature = "python")]
#[pyclass(from_py_object)]
#[derive(Debug)]
pub struct OnnxSession {
    #[pyo3(get)]
    pub schema: OnnxSchema,

    #[pyo3(get, set)]
    pub session: Option<Py<PyAny>>,

    pub quantized: bool,
}

#[cfg(feature = "python")]
#[pymethods]
impl OnnxSession {
    #[new]
    #[pyo3(signature = (model_proto, feature_names=None))]
    pub fn new(
        model_proto: &Bound<'_, PyAny>,
        feature_names: Option<Vec<String>>,
    ) -> Result<Self, OnnxError> {
        let py = model_proto.py();
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        // get model bytes for loading into rust ort
        let model_bytes = model_proto
            .call_method0("SerializeToString")?
            .extract::<Vec<u8>>()?;

        #[cfg(all(
            feature = "python",
            not(all(target_arch = "x86_64", target_os = "macos"))
        ))]
        let (input_schema, output_schema) = {
            use crate::error::OnnxError;

            let session = Session::builder()
                .map_err(OnnxError::SessionCreateError)?
                .commit_from_memory(&model_bytes)
                .map_err(OnnxError::SessionCommitError)?;
            parse_session_schema(&session)?
        };

        #[cfg(all(target_arch = "x86_64", target_os = "macos"))]
        let (input_schema, output_schema) = (FeatureSchema::default(), FeatureSchema::default());

        let schema = OnnxSchema {
            input_features: input_schema,
            output_features: output_schema,
            onnx_version,
            feature_names: feature_names.unwrap_or_default(),
        };

        // setup python onnxruntime
        let session = OnnxSession::get_py_session_from_bytes(py, &model_bytes, None)?;

        Ok(OnnxSession {
            session: Some(session),
            schema,
            quantized: false,
        })
    }

    #[setter]
    pub fn set_session(
        &mut self,
        py: Python,
        session: Option<&Bound<'_, PyAny>>,
    ) -> Result<(), OnnxError> {
        if session.is_none() {
            self.session = None;
            Ok(())
        } else {
            let rt_session = py
                .import("onnxruntime")
                .unwrap()
                .getattr("InferenceSession")?;

            // assert session is an instance of InferenceSession
            if let Some(session) = session {
                if session.is_instance(&rt_session)? {
                    self.session = Some(session.clone().unbind());
                    Ok(())
                } else {
                    Err(OnnxError::MustBeInferenceSession)
                }
            } else {
                Err(OnnxError::MustBeInferenceSession)
            }
        }
    }

    #[getter]
    pub fn get_session(&self, py: Python) -> Option<Py<PyAny>> {
        self.session.as_ref().map(|session| session.clone_ref(py))
    }

    #[pyo3(signature = (input_feed, output_names=None, run_options=None))]
    pub fn run<'py>(
        &self,
        py: Python<'py>,
        input_feed: &Bound<'py, PyDict>,
        output_names: Option<&Bound<'py, PyList>>,
        run_options: Option<&Bound<'py, PyDict>>,
    ) -> Result<Py<PyAny>, OnnxError> {
        // get session
        let sess = self.session.as_ref().ok_or(OnnxError::SessionNotFound)?;

        // call run
        let result = sess
            .call_method(py, "run", (output_names, input_feed), run_options)
            .inspect_err(|e| error!("Error running ONNX session: {}", e))?;

        Ok(result)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<(), OnnxError> {
        let onnx_bytes = std::fs::read(&path)?;
        let session = OnnxSession::get_py_session_from_bytes(py, &onnx_bytes, kwargs)?;
        self.session = Some(session);

        Ok(())
    }

    #[instrument(skip_all)]
    pub fn model_bytes(&self, py: Python) -> PyResult<Vec<u8>> {
        let sess = self.session.as_ref().ok_or(OnnxError::SessionNotFound)?;

        sess.bind(py).getattr("_model_bytes")?.extract()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> OnnxSession {
        serde_json::from_str(&json_string).unwrap()
    }
}

#[cfg(feature = "python")]
impl Clone for OnnxSession {
    fn clone(&self) -> Self {
        Python::attach(|py| {
            let new_session = self.session.as_ref().map(|session| session.clone_ref(py));
            OnnxSession {
                session: new_session,
                schema: self.schema.clone(),
                quantized: self.quantized,
            }
        })
    }
}

#[cfg(feature = "python")]
impl OnnxSession {
    /// Helper method for loading the ONNX model from a file path.
    /// This method is used internally to load the ONNX model into the session.
    ///
    /// # Arguments
    /// * `py` - Python interpreter
    /// * `proto` - Onnx ModelProto
    /// * `kwargs` - Additional keyword arguments for the session
    ///
    /// # Returns
    /// * `PyResult<Py<PyAny>>` - The loaded ONNX session
    ///
    pub fn get_py_session_from_bytes(
        py: Python,
        bytes: &[u8],
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Py<PyAny>, OnnxError> {
        let rt = py.import("onnxruntime")?;
        let providers = rt.call_method0("get_available_providers")?;

        let args = (bytes,);
        if let Some(kwargs) = kwargs {
            kwargs.set_item("providers", providers).unwrap();
        } else {
            let kwargs = PyDict::new(py);
            kwargs.set_item("providers", providers).unwrap();
        };

        let session = rt.call_method("InferenceSession", args, kwargs)?.unbind();

        debug!("Loaded ONNX model");

        Ok(session)
    }

    pub fn from_model_proto(
        model_proto: &Bound<'_, PyAny>,
        feature_names: Option<Vec<String>>,
    ) -> Result<Self, OnnxError> {
        OnnxSession::new(model_proto, feature_names)
    }

    /// Loads the ONNX model from a file path.
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `onnx_version` - Version of the ONNX model
    /// * `filepath` - Path to the ONNX model file
    /// * `feature_names` - Optional feature names
    ///
    /// # Returns
    /// * `Result<Self, TypeError>` - The loaded ONNX session
    pub fn from_file(
        py: Python,
        filepath: &Path,
        feature_names: Option<Vec<String>>,
    ) -> Result<Self, OnnxError> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        #[cfg(not(all(target_arch = "x86_64", target_os = "macos")))]
        let (input_schema, output_schema) = {
            let session = Session::builder()
                .map_err(OnnxError::SessionCreateError)?
                .commit_from_file(filepath)
                .map_err(OnnxError::SessionCommitError)?;
            parse_session_schema(&session)?
        };

        #[cfg(all(target_arch = "x86_64", target_os = "macos"))]
        let (input_schema, output_schema) = (FeatureSchema::default(), FeatureSchema::default());

        let schema = OnnxSchema {
            input_features: input_schema,
            output_features: output_schema,
            onnx_version,
            feature_names: feature_names.unwrap_or_default(),
        };

        // read onnx file to Vec<u8>
        let onnx_bytes = std::fs::read(filepath)?;

        let session = Self::get_py_session_from_bytes(py, &onnx_bytes, None)?;

        // setup python onnxruntime

        Ok(OnnxSession {
            session: Some(session),
            schema,
            quantized: false,
        })
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref session) = self.session {
            visit.call(session)?;
        }

        Ok(())
    }

    fn __clear__(&mut self) {
        self.session = None;
    }
}

#[cfg(feature = "python")]
impl Serialize for OnnxSession {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("OnnxSession", 2)?;
        // set session to none

        state.serialize_field("schema", &self.schema)?;
        state.serialize_field("quantized", &self.quantized)?;
        state.end()
    }
}

#[cfg(feature = "python")]
impl<'de> Deserialize<'de> for OnnxSession {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Schema,
            Session,
            Quantized,
        }

        struct OnnxSessionVisitor;

        impl<'de> Visitor<'de> for OnnxSessionVisitor {
            type Value = OnnxSession;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct OnnxSession")
            }

            fn visit_map<V>(self, mut map: V) -> Result<OnnxSession, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut schema = None;
                let mut session = None;
                let mut quantized = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Schema => {
                            schema = Some(map.next_value()?);
                        }
                        Field::Session => {
                            let _session: Option<serde_json::Value> = map.next_value()?;
                            session = None; // Default to None
                        }
                        Field::Quantized => {
                            quantized = Some(map.next_value()?);
                        }
                    }
                }

                let schema = schema.ok_or_else(|| de::Error::missing_field("schema"))?;
                let quantized = quantized.ok_or_else(|| de::Error::missing_field("quantized"))?;

                Ok(OnnxSession {
                    schema,
                    session,
                    quantized,
                })
            }
        }

        const FIELDS: &[&str] = &["schema", "session", "quantized"];
        deserializer.deserialize_struct("OnnxSession", FIELDS, OnnxSessionVisitor)
    }
}

#[cfg(feature = "python")]
#[pyclass(eq, from_py_object)]
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

#[cfg(feature = "python")]
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
        PyHelperFuncs::__str__(self)
    }
}
