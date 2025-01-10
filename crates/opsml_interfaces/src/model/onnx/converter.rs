use pyo3::prelude::*;

pub struct OnnxModelConverter {}

impl OnnxModelConverter {
    pub fn new() -> Self {
        OnnxModelConverter {}
    }

    pub fn convert_model(
        &self,
        model: &Bound<'_, PyAny>,
        model_type: ModelType,
    ) -> PyResult<PyObject> {
        Ok(Python::with_gil(|py| py.None()))
    }
}
