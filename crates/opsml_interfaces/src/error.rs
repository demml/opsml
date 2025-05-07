use opsml_utils::error::UtilError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum OnnxError {
    #[error("{0}")]
    Error(String),

    #[error("Failed to create onnx session: {0}")]
    SessionCreateError(ort::Error),

    #[error("Failed to commit onnx session: {0}")]
    SessionCommitError(ort::Error),

    #[error("Failed to serialize py error: {0}")]
    PySerializeError(pyo3::PyErr),

    #[error("Failed to extract model bytes: {0}")]
    PyModelBytesExtractError(pyo3::PyErr),

    #[error("Session must be an instance of InferenceSession")]
    MustBeInferenceSession,

    #[error("Session is not set. Please load an onnx model first")]
    SessionNotFound,

    #[error("Session error: {0}")]
    SessionRunError(pyo3::PyErr),

    #[error("InferenceSession error: {0}")]
    InferenceSessionError(pyo3::PyErr),

    #[error("Import error: {0}")]
    ImportError(pyo3::PyErr),

    #[error("Provider error: {0}")]
    ProviderError(pyo3::PyErr),

    #[error("Cannot save ONNX model without sample data")]
    MissingSampleData,

    #[error("Failed to convert model to ONNX: {0}")]
    PyOnnxConversionError(pyo3::PyErr),

    #[error("Failed to extract model bytes: {0}")]
    PyOnnxExtractError(pyo3::PyErr),

    #[error(transparent)]
    PyError(#[from] pyo3::PyErr),

    #[error("Failed to downcast: {0}")]
    DowncastError(String),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("No onnx file found")]
    NoOnnxFile,

    #[error("No onnx kwargs found. Onnx kwargs are required for HuggingFace models")]
    MissingOnnxKwargs,

    #[error("No ort type found. Ort type is required for HuggingFace models: {0}")]
    MissingOrtType(pyo3::PyErr),

    #[error("Failed to get quantize args: {0}")]
    QuantizeArgError(pyo3::PyErr),

    #[error("{0}")]
    LoadModelError(pyo3::PyErr),

    #[error("Model type not supported for onnx conversion")]
    ModelTypeError,
}

impl From<OnnxError> for PyErr {
    fn from(err: OnnxError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum DataInterfaceError {
    #[error(transparent)]
    PyError(#[from] pyo3::PyErr),

    #[error("Data must be a numpy array")]
    NumpyTypeError,

    #[error("No data detected in interface for saving")]
    MissingDataError,

    #[error("No data splits detected in interface for splitting")]
    MissingDataSplitsError,

    #[error("Invalid timestamp")]
    InvalidTimeStamp,

    #[error("Invalid value type. Supported types are String, Float, Int")]
    InvalidType,

    #[error("Only one split type can be provided")]
    OnlyOneSplitError,

    #[error("At least one split type must be provided")]
    AtLeastOneSplitError,

    #[error("Invalid split type")]
    InvalidSplitType,

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error("Error encountered converting polars type for feature: {0}")]
    FeatureConversionError(String),

    #[error("Invalid data type")]
    InvalidDataType,

    #[error("Data must be a pyarrow array")]
    ArrowTypeError,

    #[error("Data type not supported for profiling")]
    DataTypeNotSupportedForProfilingError,
}

impl From<DataInterfaceError> for PyErr {
    fn from(err: ModelInterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum ModelInterfaceError {
    #[error("No ONNX session detected in interface for loading")]
    OnnxSessionMissing,

    #[error("Image Processor must be an instance of BaseImageProcessor")]
    ImageProcessorValidationError,

    #[error("Tokenizer must be an instance of PreTrainedTokenizerBase")]
    TokenizerValidationError,

    #[error("Feature Extractor must be an instance of PreTrainedFeatureExtractor")]
    FeatureExtractorValidationError,

    #[error("Model must be an instance of transformers")]
    TransformerTypeError,

    #[error(transparent)]
    PyError(#[from] pyo3::PyErr),

    #[error(transparent)]
    OnnxError(#[from] OnnxError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Onnx URI not found in metadata")]
    MissingOnnxUriError,

    #[error("Preprocessor URI not found in metadata")]
    MissingPreprocessorUriError,

    #[error("Sample data URI not found in metadata")]
    MissingSampleDataUriError,

    #[error("Drift profile URI not found in metadata")]
    MissingDriftProfileUriError,

    #[error("Failed to deserialize model specific metadata: {0}")]
    DeserializeMetadataError(#[from] serde_json::Error),

    #[error("Model must be an CatBoost model or inherit from CatBoost")]
    CatBoostTypeError,

    #[error("No preprocessor detected for saving")]
    NoPreprocessorError,

    #[error("No model detected for saving")]
    NoModelError,

    #[error("Model must be an lightgbm booster or inherit from Booster. If using the Sklearn api version of LightGBMModel, use an SklearnModel interface instead")]
    LightGBMTypeError,

    #[error("Model must be an instance of a Lightning Trainer")]
    LightningTypeError,

    #[error("No trainer detected in interface for saving")]
    NoTrainerError,

    #[error(
        "LightningModel loading requires model to be passed into model kwargs for loading {{'model': {{your_model_architecture}}}}"
    )]
    LightningLoadModelError,

    #[error("Model must be an sklearn model and inherit from BaseEstimator")]
    SklearnTypeError,

    #[error("Model must be an instance of tensorflow.keras.Model")]
    TensorFlowTypeError,

    #[error("Model must be an instance of torch.nn.Module")]
    TorchTypeError,

    #[error(
        "TorchModel loading requires model to be passed into model kwargs for loading {{'model': {{your_model_architecture}}}}"
    )]
    TorchLoadModelError,

    #[error("Model must be an xgboost booster or inherit from Booster. If using the Sklearn api version of XGBoost, use the SklearnModel interface instead")]
    XGBoostTypeError,

    #[error("Drift type not found in drift profile filename: {0}")]
    DriftTypeNotFoundError(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error("Interface type not found")]
    InterfaceTypeNotFoundError,

    #[error("Model must be an Onnx ModelProto with SerializeToString method")]
    OnnxModelTypeError,

    #[error("Data must be of type tensorflow tensor or ndarray")]
    TensorFlowDataTypeError,

    #[error("Data type not supported")]
    DataTypeError,
}

impl From<ModelInterfaceError> for PyErr {
    fn from(err: ModelInterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum DataInterfaceError {}

impl From<DataInterfaceError> for PyErr {
    fn from(err: DataInterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum TypeError {
    #[error("Key {0} not found in FeatureMap")]
    MissingKeyError(String),
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
