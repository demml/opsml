use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use opsml_types::ModelType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;
use tempfile::tempdir;
use tracing::debug;

pub struct TorchOnnxConverter {}

impl Default for TorchOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl TorchOnnxConverter {
    pub fn new() -> Self {
        TorchOnnxConverter {}
    }

    fn get_onnx_session(&self, py: Python, model_path: &Path) -> Result<OnnxSession, OnnxError> {
        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        // load model_path to onnx_bytes
        OnnxSession::from_file(py, onnx_version, model_path, None)
    }

    pub fn convert_model<'py, T>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        sample_data: &T,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError>
    where
        T: OnnxExtension,
    {
        let torch_onnx = py
            .import("torch")
            .map_err(OnnxError::ImportError)?
            .getattr("onnx")?;

        debug!("Step 1: Converting torch model to ONNX");

        let onnx_data = sample_data.get_data_for_onnx(py, &ModelType::Pytorch)?;

        let tmp_dir = tempdir()?;
        // create path in temp dir
        let tmp_path = tmp_dir.path().join("model.onnx");

        torch_onnx
            .call_method("export", (model, onnx_data, &tmp_path), kwargs)
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(py, &tmp_path);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
