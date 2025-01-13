use crate::model::onnx::OnnxRegistryUpdater;
use crate::{types::ModelType, Feature, FeatureSchema, OnnxSchema, SampleData};
use opsml_error::OpsmlError;
use ort::session::Session;
use ort::value::ValueType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyList;
use tracing::debug;
pub struct SklearnPipeline {}

pub struct SklearnOnnxModelConverter {}

impl Default for SklearnOnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl SklearnOnnxModelConverter {
    pub fn new() -> Self {
        SklearnOnnxModelConverter {}
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

    fn update_registry(&self, py: Python, estimator_type: &ModelType) -> PyResult<()> {
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
    ) -> PyResult<()> {
        let model_type = ModelType::from_pyobject(&model.getattr("estimator")?);
        self.update_registry(py, &model_type)?;

        Ok(())
    }

    fn update_onnx_pipeline_registries(
        &self,
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let model_steps = model.getattr("steps")?;

        for model_step in model_steps.downcast::<PyList>()?.iter() {
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
    ) -> PyResult<()> {
        // update the stacking registry
        let estimators = model.getattr("estimators_")?;
        let final_estimator = model.getattr("final_estimator")?;
        let mut estimators_list = Vec::new();

        estimators_list.extend(estimators.downcast::<PyList>()?.iter());
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
    ) -> PyResult<()> {
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

    fn get_onnx_schema(
        &self,
        onnx_model: &Bound<'_, PyAny>,
        feature_names: Vec<String>,
    ) -> PyResult<OnnxSchema> {
        let py = onnx_model.py();

        let onnx_version = py
            .import("onnx")?
            .getattr("__version__")?
            .extract::<String>()?;

        let onnx_bytes = onnx_model
            .call_method("SerializeToString", (), None)
            .map_err(|e| OpsmlError::new_err(format!("Failed to serialize ONNX model: {}", e)))?;

        // extract onnx_bytes
        let ort_session = Session::builder()
            .map_err(|e| OpsmlError::new_err(format!("Failed to create onnx session: {}", e)))?
            .commit_from_memory(&onnx_bytes.extract::<Vec<u8>>()?)
            .map_err(|e| OpsmlError::new_err(format!("Failed to commit onnx session: {}", e)))?;

        let input_schema = ort_session
            .inputs
            .iter()
            .map(|input| {
                let name = input.name.clone();
                let input_type = input.input_type.clone();

                let feature = match input_type {
                    ValueType::Tensor {
                        ty,
                        dimensions,
                        dimension_symbols: _,
                    } => Feature::new(ty.to_string(), dimensions, None),
                    _ => Feature::new("Unknown".to_string(), vec![], None),
                };

                Ok((name, feature))
            })
            .collect::<Result<FeatureSchema, OpsmlError>>()
            .map_err(|_| OpsmlError::new_err("Failed to collect feature schema"))?;

        let output_schema = ort_session
            .outputs
            .iter()
            .map(|output| {
                let name = output.name.clone();
                let input_type = output.output_type.clone();

                let feature = match input_type {
                    ValueType::Tensor {
                        ty,
                        dimensions,
                        dimension_symbols: _,
                    } => Feature::new(ty.to_string(), dimensions, None),
                    _ => Feature::new("Unknown".to_string(), vec![], None),
                };

                Ok((name, feature))
            })
            .collect::<Result<FeatureSchema, OpsmlError>>()
            .map_err(|_| OpsmlError::new_err("Failed to collect feature schema"))?;

        Ok(OnnxSchema {
            input_features: input_schema,
            output_features: output_schema,
            onnx_version,
            feature_names,
        })
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        model_type: &ModelType,
        sample_data: &SampleData,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSchema> {
        debug!("Step 1: Updating registries for ONNX");
        self.update_sklearn_onnx_registries(py, model, model_type)?;

        let skl2onnx = py
            .import("skl2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import skl2onnx: {}", e)))?;

        let args = (model, sample_data.get_data_for_onnx(py, model_type)?);

        debug!("Step 2: Converting model to ONNX");
        let onnx_model = skl2onnx
            .call_method("to_onnx", args, kwargs)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        debug!("Step 3: Extracting ONNX schema");
        let schema = self.get_onnx_schema(&onnx_model, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        schema
    }
}
