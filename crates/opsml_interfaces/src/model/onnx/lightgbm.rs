use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use opsml_types::ModelType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::debug;
pub struct LightGBMOnnxConverter {}

impl Default for LightGBMOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl LightGBMOnnxConverter {
    pub fn new() -> Self {
        LightGBMOnnxConverter {}
    }

    fn get_onnx_session(
        &self,
        model_proto: &Bound<'_, PyAny>,
        feature_names: Vec<String>,
    ) -> Result<OnnxSession, OnnxError> {
        OnnxSession::from_model_proto(model_proto, Some(feature_names))
    }

    pub fn convert_model<'py, T>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        model_type: &ModelType,
        sample_data: &T,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError>
    where
        T: OnnxExtension,
    {
        let onnxmltools = py.import("onnxmltools").map_err(OnnxError::ImportError)?;

        let type_helper = py
            .import("skl2onnx")
            .unwrap()
            .getattr("algebra")
            .unwrap()
            .getattr("type_helper")
            .unwrap();

        debug!("Step 1: Guessing initial types");
        let initial_types = type_helper
            .call_method1(
                "guess_initial_types",
                (sample_data.get_data_for_onnx(py, model_type)?,),
            )
            .unwrap();

        debug!("Step 2: Converting lightgbm model to ONNX");
        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());
        kwargs.set_item("initial_types", initial_types).unwrap();

        let model_proto = onnxmltools
            .call_method("convert_lightgbm", (model,), Some(&kwargs))
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&model_proto, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
