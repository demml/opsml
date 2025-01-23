use crate::model::onnx::lightgbm::LightGBMOnnxModelConverter;
use crate::model::onnx::sklearn::SklearnOnnxModelConverter;
use crate::types::{ModelInterfaceType, ModelType};
use crate::{OnnxSession, SampleData};
use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use tracing::info;

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
        match model_interface_type {
            ModelInterfaceType::Sklearn => {
                info!("Converting Sklearn model to ONNX");
                let converter = SklearnOnnxModelConverter::default();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            ModelInterfaceType::LightGBM => {
                info!("Converting LightGBM model to ONNX");
                let converter = LightGBMOnnxModelConverter::default();
                converter.convert_model(py, model, model_type, sample_data)
            }
            _ => Err(OpsmlError::new_err("Model type not supported")),
        }
    }
}
