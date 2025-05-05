use crate::model::ModelInterface;
use opsml_error::OpsmlError;
use opsml_types::{ModelInterfaceType, ModelType, TaskType};
use pyo3::prelude::*;

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug)]
pub struct OnnxModel;

#[pymethods]
impl OnnxModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=None, drift_profile=None))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: Option<TaskType>,
        drift_profile: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<(Self, ModelInterface)> {
        // check if model is an onnxruntime.InferenceSession
        let rt = py
            .import("onnxruntime")
            .map_err(|e| OpsmlError::new_err(format!("Failed to import onnxruntime: {}", e)))?;

        if let Some(model) = model {
            let inference_session = rt.getattr("InferenceSession")?;
            if model.is_instance(&inference_session).map_err(|e| {
                OpsmlError::new_err(format!(
                    "Failed to check if model is an InferenceSession: {}",
                    e
                ))
            })? {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Model must be an onnxruntime.InferenceSession",
                ));
            }
        }

        let mut model_interface =
            ModelInterface::new(py, model, sample_data, task_type, drift_profile)?;
        model_interface.interface_type = ModelInterfaceType::Onnx;

        if model_interface.model_type == ModelType::Unknown {
            model_interface.model_type = ModelType::SklearnEstimator;
        }

        Ok((OnnxModel {}, model_interface))
    }
}
