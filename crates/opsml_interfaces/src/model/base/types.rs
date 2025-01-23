use opsml_error::TypeError;
use opsml_utils::{json_to_pyobject_value, pyobject_to_json};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::ser::SerializeStruct;
use serde::{Deserialize, Serialize};

#[pyclass(eq)]
#[derive(PartialEq, Debug)]
pub enum InterfaceDataType {
    Pandas,
    Polars,
    Numpy,
    Arrow,
    Torch,
}

impl InterfaceDataType {
    pub fn from_module_name(module_name: &str) -> Result<Self, TypeError> {
        match module_name {
            "pandas.core.frame.DataFrame" => Ok(InterfaceDataType::Pandas),
            "polars.dataframe.frame.DataFrame" => Ok(InterfaceDataType::Polars),
            "numpy.ndarray" => Ok(InterfaceDataType::Numpy),
            "pyarrow.lib.Table" => Ok(InterfaceDataType::Arrow),
            "torch.Tensor" => Ok(InterfaceDataType::Torch),
            "torch.utils.data.dataset.Dataset" => Ok(InterfaceDataType::Torch),
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

#[pyclass]
#[derive(Debug, Default)]
pub struct SaveArgs {
    onnx: Option<PyObject>,
    model: Option<PyObject>,
}

#[pymethods]
impl SaveArgs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None))]
    pub fn new(onnx: Option<PyObject>, model: Option<PyObject>) -> Self {
        SaveArgs { onnx, model }
    }
}

impl SaveArgs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.onnx
            .as_ref()
            .and_then(|onnx| onnx.bind(py).downcast::<PyDict>().ok())
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.model
            .as_ref()
            .and_then(|model| model.bind(py).downcast::<PyDict>().ok())
    }
}

impl Serialize for SaveArgs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::with_gil(|py| {
            let mut state = serializer.serialize_struct("SaveArgs", 2)?;
            let onnx = self
                .onnx
                .as_ref()
                .map(|onnx| pyobject_to_json(onnx.bind(py)).unwrap());
            let model = self
                .model
                .as_ref()
                .map(|model| pyobject_to_json(model.bind(py)).unwrap());

            state.serialize_field("onnx", &onnx)?;
            state.serialize_field("model", &model)?;
            state.end()
        })
    }
}

impl<'de> Deserialize<'de> for SaveArgs {
    fn deserialize<D>(deserializer: D) -> Result<SaveArgs, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct SaveArgsVisitor;

        impl<'de> serde::de::Visitor<'de> for SaveArgsVisitor {
            type Value = SaveArgs;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct SaveArgs")
            }

            fn visit_map<A>(self, mut map: A) -> Result<SaveArgs, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::with_gil(|py| {
                    let mut onnx = None;
                    let mut model = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "onnx" => {
                                onnx = Some(
                                    json_to_pyobject_value(
                                        py,
                                        &map.next_value::<serde_json::Value>()?,
                                    )
                                    .unwrap(),
                                );
                            }
                            "model" => {
                                model = Some(
                                    json_to_pyobject_value(
                                        py,
                                        &map.next_value::<serde_json::Value>()?,
                                    )
                                    .unwrap(),
                                );
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }

                    Ok(SaveArgs { onnx, model })
                })
            }
        }

        deserializer.deserialize_struct("SaveArgs", &["onnx", "model"], SaveArgsVisitor)
    }
}

impl Clone for SaveArgs {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));

            SaveArgs { onnx, model }
        })
    }
}
