use crate::{Feature, FeatureSchema, OnnxSchema};
use opsml_error::OnnxError;
use ort::session::Session;
use ort::value::ValueType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyList;

#[pyclass]
#[derive(Debug)]
pub struct OnnxSession {
    #[pyo3(get)]
    pub schema: OnnxSchema,
    pub session: PyObject,
}

#[pymethods]
impl OnnxSession {
    #[new]
    #[pyo3(signature = (onnx_version, model_bytes, feature_names=None))]
    pub fn new(
        py: Python,
        onnx_version: String,
        model_bytes: Vec<u8>,
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

        Ok(OnnxSession { session, schema })
    }

    #[pyo3(signature = (input_feed, output_names=None, run_options=None))]
    pub fn run<'py>(
        &self,
        py: Python<'py>,
        input_feed: &Bound<'py, PyDict>,
        output_names: Option<&Bound<'py, PyList>>,
        run_options: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PyObject> {
        let result = self
            .session
            .call_method(py, "run", (output_names, input_feed), run_options)
            .map_err(|e| OnnxError::Error(e.to_string()))?;

        Ok(result)
    }

    pub fn model_bytes(&self, py: Python) -> PyResult<Vec<u8>> {
        self.session
            .bind(py)
            .getattr("model_bytes")
            .map_err(|e| OnnxError::Error(e.to_string()))?
            .extract()
    }
}

impl Clone for OnnxSession {
    fn clone(&self) -> Self {
        Python::with_gil(|py| {
            let new_session = self.session.clone_ref(py);
            OnnxSession {
                session: new_session,
                schema: self.schema.clone(),
            }
        })
    }
}
