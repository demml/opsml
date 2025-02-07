use crate::model::onnx::OnnxSession;
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs;
use std::path::{Path, PathBuf};
use tracing::debug;

pub struct CatBoostOnnxModelConverter {}

impl Default for CatBoostOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl CatBoostOnnxModelConverter {
    pub fn new() -> Self {
        CatBoostOnnxModelConverter {}
    }

    fn get_onnx_session(&self, py: Python, model_path: &PathBuf) -> PyResult<OnnxSession> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        // load model_path to onnx_bytes
        let onnx_bytes = fs::read(model_path)
            .map_err(|e| OpsmlError::new_err(format!("Failed to read ONNX model: {}", e)))?;

        OnnxSession::new(py, onnx_version, onnx_bytes, "onnx".to_string(), None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        debug!("Step 1: Converting CatBoost model to ONNX");

        let args = (path,);
        let onnx_kwargs = PyDict::new(py);
        onnx_kwargs.set_item("format", "onnx")?;
        onnx_kwargs.set_item("export_parameters", kwargs)?;
        model.call_method("save_model", args, Some(&onnx_kwargs))?;

        debug!("Step 2: Extracting ONNX schema");

        let onnx_session = self.get_onnx_session(py, &path.to_path_buf());
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
