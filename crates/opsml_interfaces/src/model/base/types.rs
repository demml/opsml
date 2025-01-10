use opsml_error::TypeError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[pyclass(eq)]
#[derive(PartialEq, Debug)]
pub enum InterfaceDataType {
    Pandas,
    Polars,
    Numpy,
    Arrow,
}

impl InterfaceDataType {
    pub fn from_module_name(module_name: &str) -> Result<Self, TypeError> {
        match module_name {
            "pandas.core.frame.DataFrame" => Ok(InterfaceDataType::Pandas),
            "polars.dataframe.frame.DataFrame" => Ok(InterfaceDataType::Polars),
            "numpy.ndarray" => Ok(InterfaceDataType::Numpy),
            "pyarrow.lib.Table" => Ok(InterfaceDataType::Arrow),
            _ => Err(TypeError::Error("Invalid data type".to_string())),
        }
    }
}

#[pyclass(eq)]
#[derive(PartialEq, Serialize, Deserialize, Clone)]
pub enum TaskType {
    Classification,
    Regression,
    Clustering,
    AnomalyDetection,
    TimeSeries,
    Forecasting,
    Recommendation,
    Ranking,
    NLP,
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
    Other,
}
