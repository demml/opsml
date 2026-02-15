use crate::OnnxSession;
use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::catboost::CatBoostOnnxConverter;
use crate::model::onnx::huggingface::HuggingFaceOnnxConverter;
use crate::model::onnx::lightgbm::LightGBMOnnxConverter;
use crate::model::onnx::lightning::LightningOnnxConverter;
use crate::model::onnx::sklearn::SklearnOnnxConverter;
use crate::model::onnx::tensorflow::TensorFlowOnnxConverter;
use crate::model::onnx::torch::TorchOnnxConverter;
use crate::model::onnx::xgboost::XGBoostOnnxConverter;
use opsml_types::{ModelInterfaceType, ModelType};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;

use tracing::{debug, instrument};

pub struct OnnxModelConverter {}

impl Default for OnnxModelConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl OnnxModelConverter {
    pub fn new() -> Self {
        OnnxModelConverter {}
    }

    pub fn get_onnx_session(
        model_proto: &Bound<'_, PyAny>,
        feature_names: Vec<String>,
    ) -> Result<OnnxSession, OnnxError> {
        OnnxSession::from_model_proto(model_proto, Some(feature_names))
    }
}

pub struct OnnxConverter {}

impl OnnxConverter {
    #[instrument(skip_all, name = "convert_model_to_onnx")]
    pub fn convert_model<'py, T>(
        py: Python,
        model: &Bound<'py, PyAny>,
        sample_data: &T,
        interface_type: &ModelInterfaceType,
        model_type: &ModelType,
        path: &Path,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError>
    where
        T: OnnxExtension + std::fmt::Debug,
    {
        // check if sample data is none
        if sample_data.is_none() {
            return Err(OnnxError::MissingSampleData);
        }

        match interface_type {
            ModelInterfaceType::Sklearn => {
                debug!("Converting Sklearn model to ONNX");
                let converter = SklearnOnnxConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::LightGBM => {
                debug!("Converting LightGBM model to ONNX");
                let converter = LightGBMOnnxConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::XGBoost => {
                debug!("Converting XGBoost model to ONNX");
                let converter = XGBoostOnnxConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::Torch => {
                debug!("Converting Torch model to ONNX");
                let converter = TorchOnnxConverter::default();
                converter.convert_model(py, model, sample_data, kwargs)
            }
            ModelInterfaceType::Lightning => {
                debug!("Converting Lightning model to ONNX");
                let converter = LightningOnnxConverter::default();
                converter.convert_model(py, model, sample_data, kwargs)
            }
            ModelInterfaceType::HuggingFace => {
                debug!("Converting HuggingFace model to ONNX");
                let converter = HuggingFaceOnnxConverter::new(path);
                converter.convert_model(py, kwargs)
            }
            ModelInterfaceType::CatBoost => {
                debug!("Converting CatBoost model to ONNX");
                let converter = CatBoostOnnxConverter::default();
                converter.convert_model(py, model, path, kwargs)
            }
            ModelInterfaceType::TensorFlow => {
                debug!("Converting TensorFlow model to ONNX");
                let converter = TensorFlowOnnxConverter::default();
                converter.convert_model(py, model, kwargs)
            }

            ModelInterfaceType::Onnx => {
                debug!("Extracting Onnx model schema");
                OnnxModelConverter::get_onnx_session(model, sample_data.get_feature_names(py)?)
            }
            _ => Err(OnnxError::ModelTypeError),
        }
    }
}
