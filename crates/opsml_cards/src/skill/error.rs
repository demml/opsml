use crate::error::ArgError;
#[cfg(feature = "python")]
use pyo3::exceptions::PyRuntimeError;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::pyclass::PyClassGuardError;
use thiserror::Error;
#[cfg(feature = "python")]
use tracing::error;
#[derive(Error, Debug)]
pub enum SkillError {
    #[error("{0}")]
    Error(String),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    SerdeYamlError(#[from] serde_yaml::Error),

    #[error(transparent)]
    UtilError(#[from] opsml_utils::error::UtilError),

    #[error(transparent)]
    ArgError(#[from] ArgError),

    #[error(transparent)]
    AgentConfigError(#[from] opsml_types::error::AgentConfigError),
}

#[cfg(feature = "python")]
impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for SkillError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        SkillError::Error(err.to_string())
    }
}

#[cfg(feature = "python")]
impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for SkillError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        SkillError::DowncastError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<PyErr> for SkillError {
    fn from(err: PyErr) -> Self {
        SkillError::Error(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<SkillError> for PyErr {
    fn from(err: SkillError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<SkillError> for crate::error::CardError {
    fn from(err: SkillError) -> Self {
        crate::error::CardError::Error(err.to_string())
    }
}
