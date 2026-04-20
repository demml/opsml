use crate::{DataSaveKwargs, ModelSaveKwargs};
use opsml_types::error::TypeError;
use opsml_types::interfaces::DriftArgs;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

// Re-export types that have moved to opsml_types
pub use opsml_types::interfaces::{DataProcessor, Feature, FeatureSchema, ProcessorType};

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceModuleType {
    PretrainedModel,
    TransformerModel,
    TransformerPipeline,
}

#[pyclass(eq, from_py_object)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct PromptSaveKwargs {
    pub drift: DriftArgs,
}

#[pymethods]
impl PromptSaveKwargs {
    #[new]
    #[pyo3(signature = (drift))]
    pub fn new(drift: DriftArgs) -> Self {
        PromptSaveKwargs { drift }
    }
}

#[derive(Debug)]
/// Generic enum to use with register card methods
pub enum SaveKwargs {
    Data(DataSaveKwargs),
    Model(ModelSaveKwargs),
    Prompt(PromptSaveKwargs),
    Null,
}

impl SaveKwargs {
    pub fn from_py_kwargs(
        registry_type: &opsml_types::RegistryType,
        kwargs: Option<&Bound<'_, PyAny>>,
    ) -> Result<Self, TypeError> {
        if let Some(kwargs) = kwargs {
            match registry_type {
                opsml_types::RegistryType::Data => {
                    let data_kwargs = kwargs.extract::<DataSaveKwargs>()?;
                    Ok(SaveKwargs::Data(data_kwargs))
                }
                opsml_types::RegistryType::Model => {
                    let model_kwargs = kwargs.extract::<ModelSaveKwargs>()?;
                    Ok(SaveKwargs::Model(model_kwargs))
                }
                opsml_types::RegistryType::Prompt => {
                    let prompt_kwargs = kwargs.extract::<PromptSaveKwargs>()?;
                    Ok(SaveKwargs::Prompt(prompt_kwargs))
                }
                _ => Ok(SaveKwargs::Null),
            }
        } else {
            Ok(SaveKwargs::Null)
        }
    }

    pub fn drift_args(&self) -> Option<&DriftArgs> {
        match self {
            SaveKwargs::Model(model_kwargs) => model_kwargs.drift.as_ref(),
            SaveKwargs::Prompt(prompt_kwargs) => Some(&prompt_kwargs.drift),
            _ => None,
        }
    }

    pub fn to_py_bound<'py>(self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        match self {
            SaveKwargs::Data(data_kwargs) => data_kwargs.into_bound_py_any(py),
            SaveKwargs::Model(model_kwargs) => model_kwargs.into_bound_py_any(py),
            SaveKwargs::Prompt(prompt_kwargs) => prompt_kwargs.into_bound_py_any(py),
            SaveKwargs::Null => Ok(py.None().into_bound(py)),
        }
    }
}
