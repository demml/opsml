use opsml_crypt::error::CryptError;
use opsml_utils::error::UtilError;
#[cfg(feature = "python")]
use pyo3::PyErr;
#[cfg(feature = "python")]
use pyo3::exceptions::PyRuntimeError;
#[cfg(feature = "python")]
use pyo3::pyclass::PyClassGuardError;
#[cfg(feature = "python")]
use pythonize::PythonizeError;
use thiserror::Error;
#[cfg(feature = "python")]
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

    #[error("Workflow validation: {0}")]
    WorkflowValidation(String),

    #[error(
        "Config must be an instance of AutoQuantizationConfig, ORTConfig, or QuantizationConfig"
    )]
    HuggingFaceOnnxArgTypeError,

    #[error("Invalid onnx type")]
    InvalidOnnxType,

    #[error("{0}")]
    DowncastError(String),

    #[error("Import error: {0}")]
    ImportError(String),

    #[error("Provider error: {0}")]
    ProviderError(String),

    #[error("InferenceSession error: {0}")]
    InferenceSessionError(String),

    #[error("Invalid data type")]
    InvalidDataType,
}

#[cfg(feature = "python")]
impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for TypeError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        TypeError::DowncastError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<PythonizeError> for TypeError {
    fn from(err: PythonizeError) -> Self {
        TypeError::PyError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[cfg(feature = "python")]
impl From<PyErr> for TypeError {
    fn from(err: PyErr) -> TypeError {
        TypeError::PyError(err.to_string())
    }
}

#[cfg(feature = "python")]
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

    #[error("{0}")]
    ParseError(String),

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

    #[error(
        "Interface URL is missing. An Agent url must be provided either in the agent configuration or in the deployment configuration"
    )]
    InterfaceUrlMissing,

    #[error(
        "Interface count mismatch: Expected {expected} interfaces to match deployment URLs, but found {actual} interfaces"
    )]
    InterfaceCountMismatch { expected: usize, actual: usize },
}

#[cfg(feature = "python")]
impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for AgentConfigError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<PythonizeError> for AgentConfigError {
    fn from(err: PythonizeError) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl From<AgentConfigError> for PyErr {
    fn from(err: AgentConfigError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[cfg(feature = "python")]
impl From<PyErr> for AgentConfigError {
    fn from(err: PyErr) -> AgentConfigError {
        AgentConfigError::PyError(err.to_string())
    }
}

#[cfg(feature = "python")]
impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for AgentConfigError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        AgentConfigError::PyError(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum OnnxError {
    #[error("{0}")]
    Error(String),

    #[cfg(not(all(target_arch = "x86_64", target_os = "macos")))]
    #[error("Failed to create onnx session: {0}")]
    SessionCreateError(ort::Error),

    #[cfg(not(all(target_arch = "x86_64", target_os = "macos")))]
    #[error("Failed to commit onnx session: {0}")]
    SessionCommitError(ort::Error),

    #[error("Failed to serialize py error: {0}")]
    PySerializeError(String),

    #[error("Failed to extract model bytes: {0}")]
    PyModelBytesExtractError(String),

    #[error("Session must be an instance of InferenceSession")]
    MustBeInferenceSession,

    #[error("Session is not set. Please load an onnx model first")]
    SessionNotFound,

    #[error("Session error: {0}")]
    SessionRunError(String),

    #[error("Cannot save ONNX model without sample data")]
    MissingSampleData,

    #[error("Failed to convert model to ONNX: {0}")]
    PyOnnxConversionError(String),

    #[error("Failed to extract model bytes: {0}")]
    PyOnnxExtractError(String),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("No onnx file found")]
    NoOnnxFile,

    #[error("No onnx kwargs found. Onnx kwargs are required for HuggingFace models")]
    MissingOnnxKwargs,

    #[error("No ort type found. Ort type is required for HuggingFace models: {0}")]
    MissingOrtType(String),

    #[error("Failed to get quantize args: {0}")]
    QuantizeArgError(String),

    #[error("{0}")]
    LoadModelError(String),

    #[error("Model type not supported for onnx conversion")]
    ModelTypeError,

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for OnnxError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        OnnxError::Error(err.to_string())
    }
}

impl From<PyErr> for OnnxError {
    fn from(err: PyErr) -> Self {
        OnnxError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for OnnxError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        OnnxError::DowncastError(err.to_string())
    }
}

impl From<OnnxError> for PyErr {
    fn from(err: OnnxError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
