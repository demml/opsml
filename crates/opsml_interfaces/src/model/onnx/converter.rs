use crate::model::onnx::sklearn::SklearnOnnxModelConverter;
use crate::types::{ModelInterfaceType, ModelType};
use crate::SampleData;
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub struct OnnxModelConverter {}

impl OnnxModelConverter {
    pub fn convert_model<'py>(
        py: Python,
        model: &Bound<'py, PyAny>,
        sample_data: &SampleData,
        model_interface_type: &ModelInterfaceType,
        model_type: &ModelType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        match model_interface_type {
            ModelInterfaceType::Sklearn => {
                println!("Converting sklearn model to onnx");
                let converter = SklearnOnnxModelConverter::new(model_type);
                converter.convert_model(py, model, sample_data, kwargs)
            }
            _ => Ok(()),
        }
    }
}
