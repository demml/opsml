use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use opsml_error::OpsmlError;
use opsml_types::ModelType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs;
use std::path::PathBuf;
use tempfile::tempdir;
use tracing::debug;

pub struct LightningOnnxModelConverter {}

impl Default for LightningOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl LightningOnnxModelConverter {
    pub fn new() -> Self {
        LightningOnnxModelConverter {}
    }

    fn get_onnx_session(&self, py: Python, model_path: &PathBuf) -> PyResult<OnnxSession> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        // load model_path to onnx_bytes
        let onnx_bytes = fs::read(model_path)
            .map_err(|e| OpsmlError::new_err(format!("Failed to read ONNX model: {}", e)))?;

        OnnxSession::new(py, onnx_version, onnx_bytes, "onnx".to_string(), None, None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn convert_model<'py, T>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        sample_data: &T,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession>
    where
        T: OnnxExtension,
    {
        debug!("Step 1: Converting torch model to ONNX");

        let onnx_data = sample_data.get_data_for_onnx(py, &ModelType::Pytorch)?;

        let tmp_dir = tempdir()?;
        // create path in temp dir
        let tmp_path = tmp_dir.path().join("model.onnx");

        model
            .call_method("to_onnx", (&tmp_path, onnx_data), kwargs)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        debug!("Step 2: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(py, &tmp_path);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
