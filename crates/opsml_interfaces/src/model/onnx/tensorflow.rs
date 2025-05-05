use crate::error::OnnxError;
use crate::model::onnx::OnnxSession;
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

    fn get_onnx_session(&self, onnx_model: &Bound<'_, PyAny>) -> Result<OnnxSession, OnnxError> {
        let py = onnx_model.py();

        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        OnnxSession::from_onnx_session(onnx_version, onnx_model, None)
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

        let onnx_model = onnx_tuple.get_item(0)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&onnx_model);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
