use crate::{types::ModelType, SampleData};
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::info;

pub struct SklearnOnnxModelConverter {
    model_type: ModelType,
}

impl SklearnOnnxModelConverter {
    fn is_stacking_model_type(&self) -> bool {
        // check if the model type  is StackingEstimator, StackingClassifier, or StackingRegressor
        matches!(
            self.model_type,
            ModelType::StackingEstimator
                | ModelType::StackingClassifier
                | ModelType::StackingRegressor
        )
    }

    fn is_calibrated_classifier(&self) -> bool {
        // check if the model type is CalibratedClassifierCV or CalibratedRegressorCV
        matches!(self.model_type, ModelType::CalibratedClassifier)
    }

    fn is_pipeline_model_type(&self) -> bool {
        // check if the model type is Pipeline
        matches!(self.model_type, ModelType::SklearnPipeline)
    }

    pub fn convert_model<'py>(
        &self,
        model: &Bound<'py, PyAny>,
        sample_data: &SampleData,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        info!("Converting model to ONNX");
        // convert the model to ONNX
        let py = model.py();
        let skl2onnx = py
            .import("skl2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import skl2onnx: {}", e)))?;

        let args = (model, sample_data);

        let skl2onnx_convert = skl2onnx.call_method("to_onnx", args, kwargs)

        Ok(())
    }
}
