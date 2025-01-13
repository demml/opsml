use crate::model::onnx::sklearn::SklearnOnnxModelConverter;
use crate::types::{ModelInterfaceType, ModelType};
use crate::{OnnxSchema, SampleData};
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
    ) -> PyResult<OnnxSchema> {
        match model_interface_type {
            ModelInterfaceType::Sklearn => {
                info!("Converting Sklearn model to ONNX");
                let converter = SklearnOnnxModelConverter::new();
                converter.convert_model(py, model, model_type, sample_data, kwargs)
            }
            _ => Err(OpsmlError::new_err("Model type not supported")),
        }
    }
}