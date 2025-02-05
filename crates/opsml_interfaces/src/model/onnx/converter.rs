use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::catboost::CatBoostOnnxModelConverter;
use crate::model::onnx::huggingface::HuggingFaceOnnxModelConverter;
use crate::model::onnx::lightgbm::LightGBMOnnxModelConverter;
use crate::model::onnx::lightning::LightningOnnxModelConverter;
use crate::model::onnx::sklearn::SklearnOnnxModelConverter;
use crate::model::onnx::tensorflow::TensorFlowOnnxModelConverter;
use crate::model::onnx::torch::TorchOnnxModelConverter;
use crate::model::onnx::xgboost::XGBoostOnnxModelConverter;
use crate::types::{ModelInterfaceType, ModelType};
use crate::OnnxSession;
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;

use tracing::{debug, error, instrument};

pub struct OnnxModelConverter {}

impl OnnxModelConverter {
    #[instrument(
        skip(py, model, sample_data, model_interface_type, model_type, path, kwargs),
        name = "convert_model_to_onnx"
    )]
    pub fn convert_model<'py, T>(
        py: Python,
        model: &Bound<'py, PyAny>,
        sample_data: &T,
        model_interface_type: &ModelInterfaceType,
        model_type: &ModelType,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession>
    where
        T: OnnxExtension + std::fmt::Debug,
    {
        // check if sample data is none
        if sample_data.is_none() {
            error!("Cannot save ONNX model without sample data");
            return Err(OpsmlError::new_err(
                "Cannot save ONNX model without sample data",
            ));
        }

        match model_interface_type {
            ModelInterfaceType::Sklearn => {
                debug!("Converting Sklearn model to ONNX");
                let converter = SklearnOnnxModelConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::LightGBM => {
                debug!("Converting LightGBM model to ONNX");
                let converter = LightGBMOnnxModelConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::XGBoost => {
                debug!("Converting XGBoost model to ONNX");
                let converter = XGBoostOnnxModelConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::Torch => {
                debug!("Converting Torch model to ONNX");
                let converter = TorchOnnxModelConverter::default();
                converter.convert_model(py, model, sample_data, kwargs)
            }
            ModelInterfaceType::Lightning => {
                debug!("Converting Lightning model to ONNX");
                let converter = LightningOnnxModelConverter::default();
                converter.convert_model(py, model, sample_data, kwargs)
            }
            ModelInterfaceType::HuggingFace => {
                debug!("Converting HuggingFace model to ONNX");
                let converter = HuggingFaceOnnxModelConverter::new(path);
                converter.convert_model(py, kwargs)
            }
            ModelInterfaceType::CatBoost => {
                debug!("Converting CatBoost model to ONNX");
                let converter = CatBoostOnnxModelConverter::default();
                converter.convert_model(py, model, path, kwargs)
            }
            ModelInterfaceType::TensorFlow => {
                debug!("Converting TensorFlow model to ONNX");
                let converter = TensorFlowOnnxModelConverter::default();
                converter.convert_model(py, model, kwargs)
            }
            _ => Err(OpsmlError::new_err("Model type not supported")),
        }
    }
}
