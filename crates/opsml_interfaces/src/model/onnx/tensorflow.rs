use crate::error::OnnxError;
use crate::model::onnx::OnnxSession;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::debug;

pub struct TensorFlowOnnxConverter {}

impl Default for TensorFlowOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl TensorFlowOnnxConverter {
    pub fn new() -> Self {
        TensorFlowOnnxConverter {}
    }

    fn get_onnx_session(&self, model_proto: &Bound<'_, PyAny>) -> Result<OnnxSession, OnnxError> {
        OnnxSession::from_model_proto(model_proto, None)
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError> {
        let tf_onnx = py
            .import("tf2onnx")
            .map_err(OnnxError::ImportError)?
            .getattr("convert")?;

        debug!("Step 1: Converting tensorflow model to ONNX");

        let onnx_tuple = tf_onnx
            .call_method("from_keras", (model,), kwargs)
            .map_err(OnnxError::PyOnnxConversionError)?;

        let model_proto = onnx_tuple.get_item(0)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&model_proto);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
