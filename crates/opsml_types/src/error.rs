use opsml_crypt::error::CryptError;
use opsml_utils::error::UtilError;
use pyo3::PyErr;
use pyo3::exceptions::PyRuntimeError;
use pyo3::pyclass::PyClassGuardError;
use pythonize::PythonizeError;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum TypeError {
    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error("Invalid RegistryType")]
    InvalidRegistryType,

    #[error("Invalid type")]
    InvalidType,

    #[error("Key not found")]
    MissingKeyError,

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Metric not found: {0}")]
    NotMetricFoundError(String),

    #[error("Invalid response type")]
    InvalidResponseError,

    #[error("{0}")]
    PyError(String),

    #[error("MCP server not found")]
    McpServerNotFound(String),

    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,

    #[error("Missing MCP configuration for MCP service type")]
    MissingMCPConfig,

    #[error("Either space/name or uid must be provided")]
    MissingServiceCardArgsError,

    #[error("Registry type must be provided when card is not provided")]
    MissingRegistryTypeError,

    #[error(transparent)]
    SerdeYamlError(#[from] serde_yaml::Error),

    #[error(transparent)]
    AgentConfigError(#[from] AgentConfigError),

    #[error("Invalid card type. Expected either Card or CardPath")]
    InvalidCardType,
}

impl From<PythonizeError> for TypeError {
    fn from(err: PythonizeError) -> Self {
        TypeError::PyError(err.to_string())
    }
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for TypeError {
    fn from(err: PyErr) -> TypeError {
        TypeError::PyError(err.to_string())
    }
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for TypeError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        TypeError::PyError(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum AgentConfigError {
    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("{0}")]
    PyError(String),

    #[error(transparent)]
    SerdeYamlError(#[from] serde_yaml::Error),

    #[error("Field 'name' must be a non-empty string")]
    FieldNameEmpty,

    #[error("Field 'name' length {length} exceeds maximum allowed length of {max_length}")]
    FieldNameTooLong {
        name: String,
        length: usize,
        max_length: usize,
    },

    #[error("Field 'name' must be lowercase")]
    SkillMustBeLowercase { name: String },

    #[error("Invalid skill name '{name}': {reason}")]
    SkillNameInvalid { name: String, reason: String },

    #[error("Field 'description' must be a non-empty string")]
    FieldDescriptionEmpty,

    #[error("Field 'description' length {length} exceeds maximum allowed length of {max_length}")]
    FieldDescriptionTooLong { length: usize, max_length: usize },

    #[error("Field 'compatibility' must be a non-empty string if provided")]
    FieldCompatibilityEmpty,

    #[error("Field 'compatibility' length {length} exceeds maximum allowed length of {max_length}")]
    FieldCompatibilityTooLong { length: usize, max_length: usize },

    #[error(
        "Last directory in skills_path must match skill name, and SKILL.md must be located within that directory. Provided skills_path: {skills_path}, skill name: {skill_name}"
    )]
    LastDirectoryMustMatchSkillName {
        skills_path: String,
        skill_name: String,
    },

    #[error("SKILL.md file not found at expected path: {path}")]
    SkillFileNotFound { path: String },

    #[error("Agent configuration is missing")]
    MissingAgentConfig,

    #[error("Invalid agent configuration")]
    InvalidAgentConfig,

    #[error("Invalid skill format. Only AgentSkill and AgentSkillStandard are supported")]
    InvalidSkillFormat,
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for AgentConfigError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}

impl From<PythonizeError> for AgentConfigError {
    fn from(err: PythonizeError) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}

impl From<AgentConfigError> for PyErr {
    fn from(err: AgentConfigError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for AgentConfigError {
    fn from(err: PyErr) -> AgentConfigError {
        AgentConfigError::PyError(err.to_string())
    }
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for AgentConfigError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}
