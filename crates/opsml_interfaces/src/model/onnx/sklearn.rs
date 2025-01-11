use crate::{
    types::{ModelType, UPDATE_REGISTRY_MODELS},
    Feature, FeatureSchema, OnnxSchema, SampleData,
};
use opsml_error::OpsmlError;
use ort::session::{builder::GraphOptimizationLevel, Session};
use ort::tensor::TensorElementType;
use ort::value::ValueType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;
use tempfile::tempdir;
use tracing::info;

pub struct SklearnPipeline {}

pub struct SklearnOnnxModelConverter {
    model_type: ModelType,
}

impl SklearnOnnxModelConverter {
    pub fn new(model_type: &ModelType) -> Self {
        SklearnOnnxModelConverter {
            model_type: model_type.clone(),
        }
    }

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

    fn get_onnx_schema(&self, onnx_model: &Bound<'_, PyAny>) -> PyResult<OnnxSchema> {
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
        })
    }

    pub fn convert_model<'py>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        sample_data: &SampleData,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        info!("Converting model to ONNX");

        //self.update_sklearn_onnx_registries(py)?;
        let skl2onnx = py
            .import("skl2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import skl2onnx: {}", e)))?;

        let args = (model, sample_data.get_data_for_onnx(py)?);

        let onnx_model = skl2onnx
            .call_method("to_onnx", args, kwargs)
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        let onnx_schema = self.get_onnx_schema(&onnx_model)?;

        println!("Onnx schema: {:?}", onnx_schema);

        Ok(())
    }
}
