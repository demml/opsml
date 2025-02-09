use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::fmt::Display;
use std::fmt::Formatter;
use tracing::debug;

#[pyclass(eq)]
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
    Other,
}

impl Display for TaskType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        // match the types and return the string representation
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
            TaskType::Other => "Other",
        };

        write!(f, "{}", task_type)
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

    #[default]
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
