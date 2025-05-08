use crate::error::TypeError;
use crate::model::huggingface::types::HuggingFaceOnnxArgs;
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
            _ => Err(TypeError::InvalidDataType),
        }
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct ModelSaveKwargs {
    pub onnx: Option<Py<PyDict>>,

    pub model: Option<Py<PyDict>>,

    pub preprocessor: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub save_onnx: bool,
}

#[pymethods]
impl ModelSaveKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None, save_onnx=None))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
        save_onnx: Option<bool>,
    ) -> Result<Self, TypeError> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.downcast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.downcast::<PyDict>().unwrap().clone().unbind())
            } else {
                Err(TypeError::InvalidOnnxType)
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
            save_onnx: save_onnx.unwrap_or(false),
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
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
        serde_json::from_str(&json_string).unwrap()
    }
}

impl ModelSaveKwargs {
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

    pub fn save_onnx(&self) -> bool {
        self.save_onnx
    }
}

impl Serialize for ModelSaveKwargs {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        Python::with_gil(|py| {
            let mut state = serializer.serialize_struct("ModelSaveKwargs", 4)?;
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
            let save_onnx = self.save_onnx;

            state.serialize_field("onnx", &onnx)?;
            state.serialize_field("model", &model)?;
            state.serialize_field("preprocessor", &preprocessor)?;
            state.serialize_field("save_onnx", &save_onnx)?;
            state.end()
        })
    }
}

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
                Python::with_gil(|py| {
                    let mut onnx = None;
                    let mut model = None;
                    let mut preprocessor = None;
                    let mut save_onnx = None;

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

                            "save_onnx" => {
                                let value = map.next_value::<Option<bool>>()?;
                                save_onnx = value;
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

impl Clone for ModelSaveKwargs {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));
            let save_onnx = self.save_onnx;

            ModelSaveKwargs {
                onnx,
                model,
                preprocessor,
                save_onnx,
            }
        })
    }
}

#[pyclass]
#[derive(Debug, Default)]
pub struct ModelLoadKwargs {
    #[pyo3(get, set)]
    pub onnx: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub model: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub preprocessor: Option<Py<PyDict>>,

    #[pyo3(get, set)]
    pub load_onnx: bool,
}

#[pymethods]
impl ModelLoadKwargs {
    #[new]
    #[pyo3(signature = (onnx=None, model=None, preprocessor=None, load_onnx=false))]
    pub fn new<'py>(
        onnx: Option<Bound<'py, PyAny>>,
        model: Option<Bound<'py, PyDict>>,
        preprocessor: Option<Bound<'py, PyDict>>,
        load_onnx: Option<bool>,
    ) -> Result<Self, TypeError> {
        // check if onnx is None, PyDict or HuggingFaceOnnxArgs

        let onnx = onnx.map(|onnx| {
            if onnx.is_instance_of::<HuggingFaceOnnxArgs>() {
                let onnx_dict = onnx.call_method0("to_dict").unwrap();
                Ok(onnx_dict.downcast::<PyDict>().unwrap().clone().unbind())
            } else if onnx.is_instance_of::<PyDict>() {
                Ok(onnx.downcast::<PyDict>().unwrap().clone().unbind())
            } else {
                // return error
                Err(TypeError::InvalidOnnxType)
            }
        });

        // check for error
        let onnx = match onnx {
            Some(Ok(onnx)) => Some(onnx),
            Some(Err(e)) => return Err(e),
            None => None,
        };

        let load_onnx = if onnx.is_some() {
            load_onnx.unwrap_or(true)
        } else {
            load_onnx.unwrap_or(false)
        };

        let model = model.map(|model| model.unbind());
        let preprocessor = preprocessor.map(|preprocessor| preprocessor.unbind());
        Ok(Self {
            onnx,
            model,
            preprocessor,
            load_onnx,
        })
    }
}

impl ModelLoadKwargs {
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

impl Clone for ModelLoadKwargs {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let onnx = self.onnx.as_ref().map(|onnx| onnx.clone_ref(py));
            let model = self.model.as_ref().map(|model| model.clone_ref(py));
            let preprocessor = self
                .preprocessor
                .as_ref()
                .map(|preprocessor| preprocessor.clone_ref(py));
            let load_onnx = self.load_onnx;

            ModelLoadKwargs {
                onnx,
                model,
                preprocessor,
                load_onnx,
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
    pub fn model_validate_json(json_string: String) -> ModelSaveKwargs {
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

        deserializer.deserialize_struct("ModelSaveKwargs", &["onnx", "model"], ExtraMetadataVisitor)
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
