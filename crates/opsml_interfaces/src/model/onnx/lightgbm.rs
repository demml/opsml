use crate::model::onnx::OnnxSession;
use crate::{types::ModelType, SampleData};
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use tracing::debug;

pub struct LightGBMOnnxModelConverter {}

impl Default for LightGBMOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl LightGBMOnnxModelConverter {
    pub fn new() -> Self {
        LightGBMOnnxModelConverter {}
    }

    fn get_onnx_session(
        &self,
        onnx_model: &Bound<'_, PyAny>,
        feature_names: Vec<String>,
    ) -> PyResult<OnnxSession> {
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
            Some(feature_names),
        )
        .map_err(|e| OpsmlError::new_err(format!("Failed to create ONNX session: {}", e)))
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        model_type: &ModelType,
        sample_data: &SampleData,
    ) -> PyResult<OnnxSession> {
        debug!("Step 1: Converting lightgbm model to ONNX");

        let onnxmltools = py
            .import("onnxmltools")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import onnxmltools: {}", e)))?;

        let type_helper = py
            .import("skl2onnx")
            .unwrap()
            .getattr("algebra")
            .unwrap()
            .getattr("type_helper")
            .unwrap();

        // should return a numpy array
        let onnx_data = sample_data.get_data_for_onnx(py, model_type)?;

        debug!("Step 2: Guessing initial types");
        let initial_types = type_helper
            .call_method1("guess_initial_types", (onnx_data,))
            .unwrap();

        debug!("Step 4: Converting lightgbm model to ONNX");
        let onnx_model = onnxmltools
            .call_method("convert_lightgbm", (model, initial_types), None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        debug!("Step 5: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&onnx_model, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
