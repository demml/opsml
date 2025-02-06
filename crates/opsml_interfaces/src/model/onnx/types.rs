use std::path::PathBuf;
use std::vec;

use crate::{Feature, FeatureSchema, OnnxSchema};
use opsml_error::OnnxError;
use opsml_error::OpsmlError;
use ort::session::Session;
use ort::value::ValueType;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{PyTraverseError, PyVisit};
use serde;
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::fmt;
use tracing::debug;

#[pyclass]
#[derive(Debug)]
pub struct OnnxSession {
    #[pyo3(get)]
    pub schema: OnnxSchema,

    #[pyo3(get, set)]
    pub session: Option<PyObject>,

    pub quantized: bool,
}

#[pymethods]
impl OnnxSession {
    #[new]
    #[pyo3(signature = (onnx_version, model_bytes, onnx_type, feature_names=None))]
    pub fn new(
        py: Python,
        onnx_version: String,
        model_bytes: Vec<u8>,
        onnx_type: String,
        feature_names: Option<Vec<String>>,
    ) -> Result<Self, OnnxError> {
        // extract onnx_bytes
        let session = Session::builder()
            .map_err(|e| OnnxError::Error(format!("Failed to create onnx session: {}", e)))?
            .commit_from_memory(&model_bytes)
            .map_err(|e| OnnxError::Error(format!("Failed to commit onnx session: {}", e)))?;

        let input_schema = session
            .inputs
            .iter()
            .map(|input| {
                let name = input.name.clone();
                let input_type = input.input_type.clone();

                let feature = match input_type {
                    ValueType::Tensor {
                        ty,
                        dimensions,
                        dimension_symbols: _,
                    } => Feature::new(ty.to_string(), dimensions, None),
                    _ => Feature::new("Unknown".to_string(), vec![], None),
                };

                Ok((name, feature))
            })
            .collect::<Result<FeatureSchema, OnnxError>>()
            .map_err(|_| OnnxError::Error("Failed to collect feature schema".to_string()))?;

        let output_schema = session
            .outputs
            .iter()
            .map(|output| {
                let name = output.name.clone();
                let input_type = output.output_type.clone();

                let feature = match input_type {
                    ValueType::Tensor {
                        ty,
                        dimensions,
                        dimension_symbols: _,
                    } => Feature::new(ty.to_string(), dimensions, None),
                    _ => Feature::new("Unknown".to_string(), vec![], None),
                };

                Ok((name, feature))
            })
            .collect::<Result<FeatureSchema, OnnxError>>()
            .map_err(|_| OnnxError::Error("Failed to collect feature schema".to_string()))?;

        let schema = OnnxSchema {
            input_features: input_schema,
            output_features: output_schema,
            onnx_version,
            feature_names: feature_names.unwrap_or_default(),
            onnx_type,
        };

        // setup python onnxruntime

        let rt = py
            .import("onnxruntime")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let providers = rt
            .call_method0("get_available_providers")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let args = (model_bytes,);
        let kwargs = PyDict::new(py);
        kwargs.set_item("providers", providers).unwrap();

        let session = rt
            .call_method("InferenceSession", args, Some(&kwargs))
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .unbind();

        Ok(OnnxSession {
            session: Some(session),
            schema,
            quantized: false,
        })
    }

    #[setter]
    pub fn set_session(&mut self, py: Python, session: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        if session.is_none() {
            self.session = None;
            Ok(())
        } else {
            let rt_session = py
                .import("onnxruntime")
                .unwrap()
                .getattr("InferenceSession")
                .unwrap();

            // assert session is an instance of InferenceSession
            let session = session.unwrap();
            if session.is_instance(&rt_session).unwrap() {
                self.session = Some(session.clone().unbind());
                Ok(())
            } else {
                Err(OpsmlError::new_err(
                    "Session must be an instance of InferenceSession",
                ))
            }
        }
    }

    #[getter]
    pub fn get_session(&self, py: Python) -> Option<PyObject> {
        self.session.as_ref().map(|session| session.clone_ref(py))
    }

    #[pyo3(signature = (input_feed, output_names=None, run_options=None))]
    pub fn run<'py>(
        &self,
        py: Python<'py>,
        input_feed: &Bound<'py, PyDict>,
        output_names: Option<&Bound<'py, PyList>>,
        run_options: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PyObject> {
        let sess = self.session.as_ref().ok_or_else(|| {
            OnnxError::Error("Session is not set. Please load an onnx model first".to_string())
        })?;
        let result = sess
            .call_method(py, "run", (output_names, input_feed), run_options)
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        Ok(result)
    }

    pub fn model_bytes(&self, py: Python) -> PyResult<Vec<u8>> {
        let sess = self.session.as_ref().ok_or_else(|| {
            OnnxError::Error("Session is not set. Please load an onnx model first".to_string())
        })?;

        sess.bind(py)
            .getattr("_model_bytes")
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .extract()
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_onnx_model(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        let rt = py
            .import("onnxruntime")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let providers = rt
            .call_method0("get_available_providers")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let args = (path,);

        if let Some(kwargs) = kwargs {
            kwargs.set_item("providers", providers).unwrap();
        } else {
            let kwargs = PyDict::new(py);
            kwargs.set_item("providers", providers).unwrap();
        };

        let session = rt
            .call_method("InferenceSession", args, kwargs)
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .unbind();

        debug!("Loaded ONNX model");
        self.session = Some(session);

        Ok(())
    }
}

impl OnnxSession {
    pub fn load_onnx_session(
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let rt = py
            .import("onnxruntime")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let providers = rt
            .call_method0("get_available_providers")
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        let args = (path,);

        if let Some(kwargs) = kwargs {
            kwargs.set_item("providers", providers).unwrap();
        } else {
            let kwargs = PyDict::new(py);
            kwargs.set_item("providers", providers).unwrap();
        };

        let session = rt
            .call_method("InferenceSession", args, kwargs)
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .unbind();

        debug!("Loaded ONNX model");

        Ok(session)
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

impl Clone for OnnxSession {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let new_session = self.session.as_ref().map(|session| session.clone_ref(py));
            OnnxSession {
                session: new_session,
                schema: self.schema.clone(),
                quantized: self.quantized,
            }
        })
    }
}
