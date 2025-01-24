use opsml_error::TypeError;
use opsml_utils::{json_to_pyobject, pyobject_to_json, PyHelperFuncs};
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
pub struct SaveKwargs {
    onnx: Option<Py<PyDict>>,
    model: Option<Py<PyDict>>,
}

#[pymethods]
impl SaveKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None))]
    pub fn new<'py>(onnx: Option<Bound<'py, PyDict>>, model: Option<Bound<'py, PyDict>>) -> Self {
        let onnx = onnx.map(|onnx| onnx.unbind());
        let model = model.map(|model| model.unbind());
        Self { onnx, model }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__json__(self)
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> SaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl SaveKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().and_then(|onnx| Some(onnx.bind(py)))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.model.as_ref().and_then(|model| Some(model.bind(py)))
    }
}

impl Serialize for SaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::with_gil(|py| {
            let mut state = serializer.serialize_struct("SaveKwargs", 2)?;
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

impl<'de> Deserialize<'de> for SaveKwargs {
    fn deserialize<D>(deserializer: D) -> Result<SaveKwargs, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct SaveKwargsVisitor;

        impl<'de> serde::de::Visitor<'de> for SaveKwargsVisitor {
            type Value = SaveKwargs;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct SaveKwargs")
            }

            fn visit_map<A>(self, mut map: A) -> Result<SaveKwargs, A::Error>
            where
                A: serde::de::MapAccess<'de>,
            {
                Python::with_gil(|py| {
                    let mut onnx = None;
                    let mut model = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "onnx" => {
                                let dict = json_to_pyobject(
                                    py,
                                    &map.next_value::<serde_json::Value>()?,
                                    &PyDict::new(py),
                                )
                                .unwrap();
                                onnx = Some(dict.unbind());
                            }
                            "model" => {
                                let dict = json_to_pyobject(
                                    py,
                                    &map.next_value::<serde_json::Value>()?,
                                    &PyDict::new(py),
                                )
                                .unwrap();
                                model = Some(dict.unbind());
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }
                    let kwargs = SaveKwargs { onnx, model };
                    Ok(kwargs)
                })
            }
        }

        deserializer.deserialize_struct("SaveKwargs", &["onnx", "model"], SaveKwargsVisitor)
    }
}

impl Clone for SaveKwargs {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));

            SaveKwargs { onnx, model }
        })
    }
}
