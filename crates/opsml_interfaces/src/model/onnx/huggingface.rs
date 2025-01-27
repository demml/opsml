use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use crate::types::ModelType;
use opsml_error::OpsmlError;
use opsml_types::SaveName;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs;
use std::path::Path;
use std::path::PathBuf;
use tempfile::tempdir;
use tracing::debug;

pub struct HuggingFaceOnnxModelConverter {}

impl Default for HuggingFaceOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl HuggingFaceOnnxModelConverter {
    pub fn new() -> Self {
        HuggingFaceOnnxModelConverter {}
    }

    fn get_onnx_session(
        &self,
        py: Python,
        ort_model: &Bound<'_, PyAny>,
        model_path: &PathBuf,
    ) -> PyResult<OnnxSession> {
        // load model_path to onnx_bytes
        let onnx_bytes = fs::read(model_path)
            .map_err(|e| OpsmlError::new_err(format!("Failed to read ONNX model: {}", e)))?;

        OnnxSession::new_from_hf_session(py, ort_model, onnx_bytes)
            .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        debug!("Step 1: Converting HuggingFace model to ONNX");

        let model_save_path = path.join(SaveName::Model);
        let full_model_save_path = path.join(&model_save_path);

        let onnx_save_path = PathBuf::from(SaveName::OnnxModel);
        let full_onnx_save_path = path.join(&onnx_save_path);

        let opt_rt = py.import("optimum.onnxruntime")?;

        //let kwargs =
        //kwargs.unwrap_or_else(|| Err(OpsmlError::new_err("Onnx kwargs (HuggingFaceOnnxSaveArgs) are required for converting a HuggingFace model to Onnx")).unwrap());

        let ort_type = kwargs
            .ok_or_else(|| OpsmlError::new_err("ONNX kwargs are required"))?
            .get_item("ort_type")
            .map_err(|e| OpsmlError::new_err(format!("Failed to get ort_type: {}", e)))?
            .unwrap()
            .to_string();

        let ort_model = opt_rt.getattr(&ort_type)?.call_method(
            "from_pretrained",
            (&full_model_save_path,),
            kwargs,
        )?;

        // saves to model.onnx
        ort_model.call_method("save_pretrained", (&full_onnx_save_path,), kwargs)?;
        debug!("Step 2: Extracting ONNX schema");

        let onnx_session = self.get_onnx_session(py, &ort_model, &full_onnx_save_path);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
