use std::path::PathBuf;
use std::vec;

use crate::error::OnnxError;
use crate::{Feature, FeatureSchema, OnnxSchema};
use opsml_utils::PyHelperFuncs;
use ort::session::Session;
use ort::value::ValueType;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{PyTraverseError, PyVisit};
use serde;
use serde::{
    Deserialize, Deserializer, Serialize, Serializer,
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
};
use std::fmt;
use std::path::Path;
use tracing::{debug, instrument};

/// Extracts input and output schema from the ort ONNX session.
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

#[pyclass]
#[derive(Debug)]
pub struct OnnxSession {
    #[pyo3(get)]
    pub schema: OnnxSchema,

    #[pyo3(get, set)]
    pub session: Option<Py<PyAny>>,

    pub quantized: bool,
}

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
            .call_method0("SerializeToString")
            .map_err(OnnxError::PySerializeError)?
            .extract::<Vec<u8>>()
            .map_err(OnnxError::PyModelBytesExtractError)?;

        // extract onnx_bytes
        let session = Session::builder()
            .map_err(OnnxError::SessionCreateError)?
            .commit_from_memory(&model_bytes)
            .map_err(OnnxError::SessionCommitError)?;

        let (input_schema, output_schema) = parse_session_schema(&session)?;

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
        let sess = self
            .session
            .as_ref()
            .ok_or_else(|| OnnxError::SessionNotFound)?;

        // call run
        let result = sess
            .call_method(py, "run", (output_names, input_feed), run_options)
            .map_err(OnnxError::SessionRunError)?;

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
        let sess = self
            .session
            .as_ref()
            .ok_or_else(|| OnnxError::SessionNotFound)?;

        sess.bind(py)
            .getattr("_model_bytes")
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .extract()
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
        let rt = py.import("onnxruntime").map_err(OnnxError::ImportError)?;

        let providers = rt
            .call_method0("get_available_providers")
            .map_err(OnnxError::ProviderError)?;

        let args = (bytes,);
        if let Some(kwargs) = kwargs {
            kwargs.set_item("providers", providers).unwrap();
        } else {
            let kwargs = PyDict::new(py);
            kwargs.set_item("providers", providers).unwrap();
        };

        let session = rt
            .call_method("InferenceSession", args, kwargs)
            .map_err(OnnxError::InferenceSessionError)?
            .unbind();

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
    /// * `Result<Self, OnnxError>` - The loaded ONNX session
    pub fn from_file(
        py: Python,
        filepath: &Path,
        feature_names: Option<Vec<String>>,
    ) -> Result<Self, OnnxError> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        let session = Session::builder()
            .map_err(OnnxError::SessionCreateError)?
            .commit_from_file(filepath)
            .map_err(OnnxError::SessionCommitError)?;

        let (input_schema, output_schema) = parse_session_schema(&session)?;

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
