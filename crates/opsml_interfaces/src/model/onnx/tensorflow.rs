use crate::base::OnnxExtension;
use crate::model::onnx::OnnxSession;
use crate::ModelType;
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::debug;

pub struct TensorFlowOnnxModelConverter {}

impl Default for TensorFlowOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl TensorFlowOnnxModelConverter {
    pub fn new() -> Self {
        TensorFlowOnnxModelConverter {}
    }

    fn get_onnx_session(&self, onnx_model: &Bound<'_, PyAny>) -> PyResult<OnnxSession> {
        let py = onnx_model.py();

        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        let onnx_bytes = onnx_model
            .call_method("SerializeToString", (), None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to serialize ONNX model: {}", e)))?;

        OnnxSession::new(
            py,
            onnx_version,
            onnx_bytes.extract::<Vec<u8>>()?,
            "onnx".to_string(),
            None,
        )
        .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        let tf_onnx = py
            .import("tf2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import tf2onnx: {:?}", e)))?
            .getattr("convert")?;

        debug!("Step 1: Converting tensorflow model to ONNX");

        println!("kwargs: {:?}", kwargs);

        let onnx_tuple = tf_onnx
            .call_method("from_keras", (model,), kwargs)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        let onnx_model = onnx_tuple.get_item(0).map_err(|e| {
            OpsmlError::new_err(format!("Failed to extract ONNX model from tuple: {}", e))
        })?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&onnx_model);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
