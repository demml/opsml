use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::{OnnxRegistryUpdater, OnnxSession};
use opsml_types::ModelType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyList;
use tracing::debug;

pub struct SklearnOnnxConverter {}

impl Default for SklearnOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl SklearnOnnxConverter {
    pub fn new() -> Self {
        SklearnOnnxConverter {}
    }

    fn is_stacking_model_type(&self, model_type: &ModelType) -> bool {
        // check if the model type  is StackingEstimator, StackingClassifier, or StackingRegressor
        matches!(
            model_type,
            ModelType::StackingEstimator
                | ModelType::StackingClassifier
                | ModelType::StackingRegressor
        )
    }

    fn is_calibrated_classifier(&self, model_type: &ModelType) -> bool {
        // check if the model type is CalibratedClassifierCV or CalibratedRegressorCV
        matches!(model_type, ModelType::CalibratedClassifier)
    }

    fn is_pipeline_model_type(&self, model_type: &ModelType) -> bool {
        // check if the model type is Pipeline
        matches!(model_type, ModelType::SklearnPipeline)
    }

    fn update_registry(&self, py: Python, estimator_type: &ModelType) -> Result<(), OnnxError> {
        if estimator_type.in_update_registry() {
            OnnxRegistryUpdater::update_registry(py, estimator_type)?;
        }

        Ok(())
    }

    /// Update the ONNX registries for calibrated classifiers
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter
    /// * `model` - Model object (this is the calibrated classifier model)
    fn update_onnx_calibrated_classifier_registries<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
    ) -> Result<(), OnnxError> {
        let model_type = ModelType::from_pyobject(&model.getattr("estimator")?);
        self.update_registry(py, &model_type)?;

        Ok(())
    }

    fn update_onnx_pipeline_registries(
        &self,
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> Result<(), OnnxError> {
        let model_steps = model.getattr("steps")?;

        for model_step in model_steps.cast::<PyList>()?.iter() {
            let mut estimator_type = ModelType::from_pyobject(&model_step.get_item(1)?);

            debug!(
                "Updating pipeline registries for ONNX: {:?}",
                estimator_type
            );

            if estimator_type == ModelType::CalibratedClassifier {
                estimator_type =
                    ModelType::from_pyobject(&model_step.get_item(1)?.getattr("estimator")?);
            }

            self.update_registry(py, &estimator_type)?;
        }

        Ok(())
    }

    fn update_onnx_stacking_registries(
        &self,
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> Result<(), OnnxError> {
        // update the stacking registry
        let estimators = model.getattr("estimators_")?;
        let final_estimator = model.getattr("final_estimator")?;
        let mut estimators_list = Vec::new();

        estimators_list.extend(estimators.cast::<PyList>()?.iter());
        estimators_list.push(final_estimator);

        for estimator in estimators_list {
            let mut estimator_type = ModelType::from_pyobject(&estimator);

            if estimator_type == ModelType::CalibratedClassifier {
                estimator_type = ModelType::from_pyobject(&estimator.getattr("estimator")?);
            }

            self.update_registry(py, &estimator_type)?;
        }

        Ok(())
    }

    fn update_sklearn_onnx_registries(
        &self,
        py: Python,
        model: &Bound<'_, PyAny>,
        model_type: &ModelType,
    ) -> Result<(), OnnxError> {
        if self.is_pipeline_model_type(model_type) {
            debug!("Updating pipeline registries for ONNX");
            self.update_onnx_pipeline_registries(py, model)
            // update the pipeline registry
        } else if self.is_stacking_model_type(model_type) {
            debug!("Updating stacking registries for ONNX");
            self.update_onnx_stacking_registries(py, model)

            // update the stacking registry
        } else if self.is_calibrated_classifier(model_type) {
            debug!("Updating calibrated registries for ONNX");
            self.update_onnx_calibrated_classifier_registries(py, model)
            // update the calibrated classifier registry
        } else {
            let estimator_type = ModelType::from_pyobject(model);
            self.update_registry(py, &estimator_type)
        }
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
        debug!("Step 1: Updating registries for ONNX");
        self.update_sklearn_onnx_registries(py, model, model_type)?;

        let skl2onnx = py.import("skl2onnx").map_err(OnnxError::ImportError)?;

        let args = (model, sample_data.get_data_for_onnx(py, model_type)?);

        debug!("Step 2: Converting model to ONNX");
        let model_proto = skl2onnx
            .call_method("to_onnx", args, kwargs)
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&model_proto, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
