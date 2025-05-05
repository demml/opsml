use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use opsml_types::ModelType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
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
    ) -> Result<OnnxSession, OnnxError> {
        let py = onnx_model.py();

        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        OnnxSession::from_onnx_session(onnx_version, onnx_model, Some(feature_names))
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

        let onnx_model = onnxmltools
            .call_method("convert_lightgbm", (model,), Some(&kwargs))
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&onnx_model, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
