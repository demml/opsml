use crate::model::ModelInterface;
use crate::model::TaskType;
use crate::types::{FeatureSchema, ModelInterfaceType};
use opsml_error::OpsmlError;
use pyo3::prelude::*;

#[pyclass(extends=ModelInterface, subclass)]
#[derive(Debug, Clone)]
pub struct SklearnModel {}

#[pymethods]
impl SklearnModel {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (model=None, sample_data=None, task_type=TaskType::Other, schema=None,))]
    pub fn new<'py>(
        py: Python,
        model: Option<&Bound<'py, PyAny>>,
        sample_data: Option<&Bound<'py, PyAny>>,
        task_type: TaskType,
        schema: Option<FeatureSchema>,
    ) -> PyResult<(Self, ModelInterface)> {
        // check if model is base estimator for sklearn validation
        if let Some(model) = model {
            let base_estimator = py
                .import("sklearn")?
                .getattr("base")?
                .getattr("BaseEstimator")?;
            if model.is_instance(&base_estimator).unwrap() {
                //
            } else {
                return Err(OpsmlError::new_err(
                    "Sample data must be an sklearn model and inherit from BaseEstimator",
                ));
            }
        }

        let mut model_interface = ModelInterface::new(py, model, sample_data, task_type, schema)?;

        model_interface.model_interface_type = ModelInterfaceType::Sklearn;

        Ok((SklearnModel {}, model_interface))
    }
}
