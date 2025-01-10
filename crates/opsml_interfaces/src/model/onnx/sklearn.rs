use crate::{
    types::{ModelType, UPDATE_REGISTRY_MODELS},
    SampleData,
};
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::info;

pub struct SklearnPipeline {}

pub struct SklearnOnnxModelConverter {
    model_type: ModelType,
    model: PyObject,
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

    fn update_onnx_calibrated_classifier_registries(
        &self,
        model: &Bound<'_, PyAny>,
        estimator: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let mut updated = false;

        // if estimator is none, set it to the model
        let estimator = if estimator.is_none() {
            model
        } else {
            estimator
        };

        let estimator_name = estimator
            .getattr("__class__")?
            .getattr("__name__")?
            .extract::<String>()?;

        let model_type = ModelType::get_type(&estimator_name);

        if model_type.in_update_registry() {
            // update the registry
            updated = true;
        }

        Ok(())
    }

    fn update_onnx_pipeline_registries(&self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        let mut updated = false;

        for model_step in model.getattr("steps") {
            // estimator_name = model_step[1].__class__.__name__
            let estimator_name = model_step
                .get_item(1)?
                .getattr("__class__")?
                .getattr("__name__")?
                .extract::<String>()?;

            if estimator_name == ModelType::CalibratedClassifier.to_string() {
                self.update_onnx_calibrated_classifier_registries(
                    model,
                    &model_step.get_item(1)?.getattr("estimator")?,
                )?;
            }
        }

        Ok(())
    }

    fn update_sklearn_onnx_registries(&self, model: &Bound<'_, PyAny>) -> PyResult<()> {
        // update the sklearn-onnx registry

        if self.is_pipeline_model_type() {
            // update the pipeline registry
        } else if self.is_stacking_model_type() {
            // update the stacking registry
        } else if self.is_calibrated_classifier() {
            // update the calibrated classifier registry
        }
        Ok(())
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

        self.update_sklearn_onnx_registries(py)?;

        let skl2onnx = py
            .import("skl2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import skl2onnx: {}", e)))?;

        let args = (model, sample_data.get_data_for_onnx(py)?);

        let onnx_model = skl2onnx
            .call_method("to_onnx", args, kwargs)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        // save to tmp path for loading

        // create onnx session

        // get feature dictionary from session

        Ok(())
    }
}
