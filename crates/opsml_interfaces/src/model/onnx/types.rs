use crate::{Feature, FeatureSchema, OnnxSchema};
use opsml_error::OnnxError;
use ort::session::Session;
use ort::value::ValueType;
use pyo3::prelude::*;

use pyo3::types::PyDict;

pub struct OnnxSession {
    pub schema: OnnxSchema,
    pub session: PyObject,
}

impl OnnxSession {
    pub fn new(
        py: Python,
        onnx_version: String,
        model_bytes: &Vec<u8>,
        feature_names: Option<&Vec<String>>,
    ) -> Result<Self, OnnxError> {
        // extract onnx_bytes
        let session = Session::builder()
            .map_err(|e| OnnxError::Error(format!("Failed to create onnx session: {}", e)))?
            .commit_from_memory(model_bytes)
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
            feature_names: feature_names.unwrap_or(&vec![]).to_vec(),
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
}
