use crate::model::huggingface::types::HuggingFaceOnnxArgs;
use opsml_error::{OpsmlError, TypeError};
use opsml_utils::{json_to_pyobject, pyobject_to_json, PyHelperFuncs};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::ser::SerializeStruct;
use serde::{Deserialize, Serialize};
use serde_json::json;
use serde_json::Value;

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
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
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
    pub onnx: Option<Py<PyDict>>,
    pub model: Option<Py<PyDict>>,
    pub preprocessor: Option<Py<PyDict>>,
}

#[pymethods]
impl SaveKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
    ) -> PyResult<Self> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.downcast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.downcast::<PyDict>().unwrap().clone().unbind())
            } else {
                Err(OpsmlError::new_err("Invalid onnx type"))
            }
        });

        let onnx = match onnx {
            Some(Ok(onnx)) => Some(onnx),
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
        })
    }

    pub fn __str__(&self, py: Python) -> String {
        let mut onnx = Value::Null;
        let mut model = Value::Null;
        let mut preprocessor = Value::Null;

        if let Some(onnx_args) = &self.onnx {
            onnx = pyobject_to_json(onnx_args.bind(py)).unwrap();
        }

        if let Some(model_args) = &self.model {
            model = pyobject_to_json(model_args.bind(py)).unwrap();
        }

        if let Some(preprocessor_args) = &self.preprocessor {
            preprocessor = pyobject_to_json(preprocessor_args.bind(py)).unwrap();
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
    pub fn model_validate_json(json_string: String) -> SaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl SaveKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().map(|onnx| onnx.bind(py))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.model.as_ref().map(|model| model.bind(py))
    }

    pub fn preprocessor_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.bind(py))
    }
}

impl Serialize for SaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::with_gil(|py| {
            let mut state = serializer.serialize_struct("SaveKwargs", 3)?;
            let onnx = self
                .onnx
                .as_ref()
                .map(|onnx| pyobject_to_json(onnx.bind(py)).unwrap());
            let model = self
                .model
                .as_ref()
                .map(|model| pyobject_to_json(model.bind(py)).unwrap());
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| pyobject_to_json(preprocessor.bind(py)).unwrap());

            state.serialize_field("onnx", &onnx)?;
            state.serialize_field("model", &model)?;
            state.serialize_field("preprocessor", &preprocessor)?;
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
                    let mut preprocessor = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "onnx" => {
                                let value = map.next_value::<serde_json::Value>()?;
                                match value {
                                    serde_json::Value::Null => {
                                        onnx = None;
                                    }
                                    _ => {
                                        let dict =
                                            json_to_pyobject(py, &value, &PyDict::new(py)).unwrap();
                                        onnx = Some(dict.unbind());
                                    }
                                }
                            }
                            "model" => {
                                let value = map.next_value::<serde_json::Value>()?;
                                match value {
                                    serde_json::Value::Null => {
                                        model = None;
                                    }
                                    _ => {
                                        let dict =
                                            json_to_pyobject(py, &value, &PyDict::new(py)).unwrap();
                                        model = Some(dict.unbind());
                                    }
                                }
                            }
                            "preprocessor" => {
                                let value = map.next_value::<serde_json::Value>()?;
                                match value {
                                    serde_json::Value::Null => {
                                        preprocessor = None;
                                    }
                                    _ => {
                                        let dict =
                                            json_to_pyobject(py, &value, &PyDict::new(py)).unwrap();
                                        preprocessor = Some(dict.unbind());
                                    }
                                }
                            }
                            _ => {
                                let _: serde::de::IgnoredAny = map.next_value()?;
                            }
                        }
                    }
                    let kwargs = SaveKwargs {
                        onnx,
                        model,
                        preprocessor,
                    };
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
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));

            SaveKwargs {
                onnx,
                model,
                preprocessor,
            }
        })
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct LoadKwargs {
    #[pyo3(get, set)]
    onnx: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    model: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    preprocessor: Option<Py<PyDict>>,
}

#[pymethods]
impl LoadKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
    ) -> PyResult<Self> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.downcast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.downcast::<PyDict>().unwrap().clone().unbind())
            } else {
                // return error
                Err(OpsmlError::new_err("Invalid onnx type"))
            }
        });

        // check for error
        let onnx = match onnx {
            Some(Ok(onnx)) => Some(onnx),
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
        })
    }
}

impl LoadKwargs {
    pub fn onnx_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.onnx.as_ref().map(|onnx| onnx.bind(py))
    }

    pub fn model_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.model.as_ref().map(|model| model.bind(py))
    }

    pub fn preprocessor_kwargs<'py>(&self, py: Python<'py>) -> Option<&Bound<'py, PyDict>> {
        // convert Option<PyObject> into Option<Bound<_, PyDict>>
        self.preprocessor
            .as_ref()
            .map(|preprocessor| preprocessor.bind(py))
    }
}

impl Clone for LoadKwargs {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));

            LoadKwargs {
                onnx,
                model,
                preprocessor,
            }
        })
    }
}

#[pyclass]
#[derive(Debug)]
pub struct ExtraMetadata {
    metadata: Py<PyDict>,
}

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
    pub fn model_validate_json(json_string: String) -> SaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl Serialize for ExtraMetadata {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::with_gil(|py| {
            let mut state = serializer.serialize_struct("ExtraMetadata", 1)?;
            let metadata = pyobject_to_json(self.metadata.bind(py)).unwrap();

            state.serialize_field("metadata", &metadata)?;
            state.end()
        })
    }
}

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
                Python::with_gil(|py| {
                    let mut metadata = None;

                    while let Some(key) = map.next_key::<String>()? {
                        match key.as_str() {
                            "metadata" => {
                                let value = map.next_value::<serde_json::Value>()?;
                                match value {
                                    serde_json::Value::Null => {
                                        metadata = None;
                                    }
                                    _ => {
                                        let dict =
                                            json_to_pyobject(py, &value, &PyDict::new(py)).unwrap();
                                        metadata = Some(dict.unbind());
                                    }
                                }
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

        deserializer.deserialize_struct("SaveKwargs", &["onnx", "model"], ExtraMetadataVisitor)
    }
}

impl Clone for ExtraMetadata {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let metadata = self.metadata.clone_ref(py);

            ExtraMetadata { metadata }
        })
    }
}
