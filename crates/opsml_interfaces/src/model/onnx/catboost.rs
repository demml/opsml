use crate::error::OnnxError;
use crate::model::onnx::OnnxSession;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;
use tracing::debug;

pub struct CatBoostOnnxConverter {}

impl Default for CatBoostOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl CatBoostOnnxConverter {
    pub fn new() -> Self {
        CatBoostOnnxConverter {}
    }

    fn get_onnx_session(&self, py: Python, model_path: &Path) -> Result<OnnxSession, OnnxError> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        OnnxSession::from_file(py, onnx_version, model_path, None)
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError> {
        debug!("Step 1: Converting CatBoost model to ONNX");

        let args = (path,);
        let onnx_kwargs = PyDict::new(py);
        onnx_kwargs.set_item("format", "onnx")?;
        onnx_kwargs.set_item("export_parameters", kwargs)?;
        model.call_method("save_model", args, Some(&onnx_kwargs))?;

        debug!("Step 2: Extracting ONNX schema");

        let onnx_session = self.get_onnx_session(py, path);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
