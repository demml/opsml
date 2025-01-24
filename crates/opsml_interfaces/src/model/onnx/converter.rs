use crate::model::onnx::lightgbm::LightGBMOnnxModelConverter;
use crate::model::onnx::sklearn::SklearnOnnxModelConverter;
use crate::model::onnx::xgboost::XGBoostOnnxModelConverter;
use crate::types::{ModelInterfaceType, ModelType};
use crate::{OnnxSession, SampleData};
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::{debug, span, Level};

pub struct OnnxModelConverter {}

impl OnnxModelConverter {
    pub fn convert_model<'py>(
        py: Python,
        model: &Bound<'py, PyAny>,
        sample_data: &SampleData,
        model_interface_type: &ModelInterfaceType,
        model_type: &ModelType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<OnnxSession> {
        let span = span!(Level::DEBUG, "Onnx Conversion");
        let _enter = span.enter();

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
            _ => Err(OpsmlError::new_err("Model type not supported")),
        }
    }
}
