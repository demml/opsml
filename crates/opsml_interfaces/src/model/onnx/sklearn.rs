use crate::model::onnx::OnnxRegistryUpdater;
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
use pyo3::types::PyList;
use std::collections::HashMap;
use std::path::PathBuf;
use tempfile::tempdir;
use tracing::{debug, info};

pub struct SklearnPipeline {}

pub struct SklearnOnnxModelConverter {
    model_type: ModelType,
    opsets: HashMap<String, i64>,
}

impl SklearnOnnxModelConverter {
    pub fn new(model_type: &ModelType) -> Self {
        SklearnOnnxModelConverter {
            model_type: model_type.clone(),
            opsets: HashMap::new(),
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

    fn update_onnx_calibrated_classifier_registries<'py>(
        &mut self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        estimator: &Bound<'py, PyAny>,
    ) -> PyResult<bool> {
        let mut updated = false;

        // if estimator is none, set it to the model
        let estimator = if estimator.is_none() {
            model
        } else {
            estimator
        };

        let model_type = ModelType::from_pyobject(estimator);
        let onnx_type = model_type.get_onnx_update_type();

        if onnx_type.in_update_registry() {
            // update the registry
            OnnxRegistryUpdater::update_registry(py, &onnx_type)?;

            // lightgbm and xgboost require different opsets
            self.opsets.insert("ai.onnx.ml".to_string(), 3);
            self.opsets.insert("".to_string(), 19);

            updated = true;
        }

        Ok(updated)
    }

    fn update_onnx_pipeline_registries(
        &mut self,
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let model_steps = model.getattr("steps")?;

        for model_step in model_steps.downcast::<PyList>()?.iter() {
            let estimator_type = ModelType::from_pyobject(&model_step.get_item(1)?);

            debug!(
                "Updating pipeline registries for ONNX: {:?}",
                estimator_type
            );

            match estimator_type {
                ModelType::CalibratedClassifier => {
                    self.update_onnx_calibrated_classifier_registries(
                        py,
                        model,
                        &model_step.get_item(1)?.getattr("estimator")?,
                    )?;
                }
                _ => {
                    // check if the model type is in the update registry models
                    if estimator_type.in_update_registry() {
                        // lightgbm and xgboost require different opsets
                        // lightgbm and xgboost require different opsets
                        self.opsets.insert("ai.onnx.ml".to_string(), 3);
                        self.opsets.insert("".to_string(), 19);

                        // update the registry
                        OnnxRegistryUpdater::update_registry(py, &estimator_type)?;
                    }
                }
            }
        }

        Ok(())
    }

    fn update_sklearn_onnx_registries(
        &mut self,
        py: Python,
        model: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        // update the sklearn-onnx registry

        if self.is_pipeline_model_type() {
            debug!("Updating pipeline registries for ONNX");
            self.update_onnx_pipeline_registries(py, model)?
            // update the pipeline registry
        } else if self.is_stacking_model_type() {
            // update the stacking registry
        } else if self.is_calibrated_classifier() {
            // update the calibrated classifier registry
        }
        Ok(())
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
        &mut self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        sample_data: &SampleData,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSchema> {
        let model_type = ModelType::from_pyobject(model);

        let mut kwargs = if kwargs.is_none() {
            PyDict::new(py)
        } else {
            kwargs.unwrap().clone()
        };

        info!("Converting model to ONNX for model type: {:?}", model_type);

        self.update_sklearn_onnx_registries(py, model)?;

        //self.update_sklearn_onnx_registries(py)?;
        let skl2onnx = py
            .import("skl2onnx")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import skl2onnx: {}", e)))?;

        if !self.opsets.is_empty() {
            kwargs.set_item("target_opset", self.opsets.clone())?;
        }

        let args = (model, sample_data.get_data_for_onnx(py, &model_type)?);

        let onnx_model = skl2onnx
            .call_method("to_onnx", args, Some(&kwargs))
            .map_err(|e| OpsmlError::new_err(format!("Failed to convert model to ONNX: {}", e)))?;

        debug!("ONNX model converted");
        self.get_onnx_schema(&onnx_model, sample_data.get_feature_names(py)?)
    }
}
