use opsml_utils::error::UtilError;
use pyo3::PyErr;
use pyo3::exceptions::PyRuntimeError;
use pyo3::pyclass::PyClassGuardError;
use pythonize::PythonizeError;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum TypeError {
    #[error("{0}")]
    Error(String),

    #[error("Key {0} not found in FeatureMap")]
    MissingKeyError(String),

    #[error("Only one of query or filename can be provided")]
    OnlyOneQueryorFilenameError,

    #[error("Key not found")]
    KeyNotFound,

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Invalid data type")]
    InvalidDataType,

    #[error("Invalid onnx type")]
    InvalidOnnxType,
}

impl From<TypeError> for PyErr {
    fn from(err: TypeError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for TypeError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        TypeError::Error(err.to_string())
    }
}

#[derive(Error, Debug)]
pub enum DataInterfaceError {
    #[error("{0}")]
    Error(String),

    #[error("Data must be a numpy array. Received: {0}")]
    NumpyTypeError(String),

    #[error("Data must be a pandas dataframe. Received: {0}")]
    PandasTypeError(String),

    #[error("Data must be a polars.DataFrame. Received: {0}")]
    PolarsTypeError(String),

    #[error("Data must be a Torch tensor. Received: {0}")]
    TorchTypeError(String),

    #[error("Torch dataset requires kwargs with torch_dataset")]
    MissingTorchKwargsError,

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
    DataProfileError(#[from] scouter_client::DataProfileError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error("Error encountered converting polars type for feature: {0}")]
    FeatureConversionError(String),

    #[error("Invalid data type")]
    InvalidDataType,

    #[error("Data must be a pyarrow array")]
    ArrowTypeError,

    #[error("Data type not supported for profiling")]
    DataTypeNotSupportedForProfilingError,

    #[error("Failed to save scouter profile")]
    ScouterSaveError(#[source] scouter_client::UtilError),

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for DataInterfaceError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        DataInterfaceError::Error(err.to_string())
    }
}

impl From<PyErr> for DataInterfaceError {
    fn from(err: PyErr) -> Self {
        DataInterfaceError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for DataInterfaceError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        DataInterfaceError::DowncastError(err.to_string())
    }
}

impl From<DataInterfaceError> for PyErr {
    fn from(err: DataInterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

#[derive(Error, Debug)]
pub enum SampleDataError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    DataInterfaceError(#[from] DataInterfaceError),

    #[error("Invalid data type")]
    InvalidDataType,

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Data must be of type tensorflow tensor or ndarray")]
    TensorFlowDataTypeError,

    #[error("Data must be of type torch tensor")]
    TorchDataTypeError,

    #[error("Data type not supported")]
    DataTypeError,
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for SampleDataError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        SampleDataError::Error(err.to_string())
    }
}

impl From<PyErr> for SampleDataError {
    fn from(err: PyErr) -> Self {
        SampleDataError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for SampleDataError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        SampleDataError::DowncastError(err.to_string())
    }
}

impl From<SampleDataError> for PyErr {
    fn from(err: SampleDataError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

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
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    SampleDataError(#[from] SampleDataError),

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

#[derive(Error, Debug)]
pub enum ModelInterfaceError {
    #[error("{0}")]
    Error(String),

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
    OnnxError(#[from] OnnxError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    SampleDataError(#[from] SampleDataError),

    #[error(transparent)]
    DriftProfileError(#[from] scouter_client::DriftError),

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

    #[error(
        "Model must be an lightgbm booster or inherit from Booster. If using the Sklearn api version of LightGBMModel, use an SklearnModel interface instead"
    )]
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

    #[error(
        "Model must be an xgboost booster or inherit from Booster. If using the Sklearn api version of XGBoost, use the SklearnModel interface instead"
    )]
    XGBoostTypeError,

    #[error("Drift type not found in drift profile filename: {0}")]
    DriftTypeNotFoundError(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    DataInterfaceError(#[from] DataInterfaceError),

    #[error("Interface type not found")]
    InterfaceTypeNotFoundError,

    #[error("Model must be an Onnx ModelProto with SerializeToString method")]
    OnnxModelTypeError,

    #[error(
        "Config must be an instance of AutoQuantizationConfig, ORTConfig, or QuantizationConfig"
    )]
    HuggingFaceOnnxArgTypeError,

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Drift profile argument must be a dictionary of alias with drift profile, list of drift profiles with aliases or a single drift profile with and alias")]
    DriftProfileNotFound,

    #[error("Drift profile not found in map")]
    DriftProfileNotFoundInMap,

    #[error("Drift profile alias must be set when passing list of drift profiles")]
    DriftProfileListAliasMustBeSet,

    #[error("Drift profile alias must be set when passing drift profile")]
    DriftProfileAliasMustBeSet,
}

impl From<PythonizeError> for ModelInterfaceError {
    fn from(err: PythonizeError) -> Self {
        ModelInterfaceError::Error(err.to_string())
    }
}

impl<'a, 'py> From<pyo3::CastError<'a, 'py>> for ModelInterfaceError {
    fn from(err: pyo3::CastError<'a, 'py>) -> Self {
        ModelInterfaceError::DowncastError(err.to_string())
    }
}

impl<'a, 'py> From<PyClassGuardError<'a, 'py>> for ModelInterfaceError {
    fn from(err: PyClassGuardError<'a, 'py>) -> Self {
        ModelInterfaceError::Error(err.to_string())
    }
}

impl From<PyErr> for ModelInterfaceError {
    fn from(err: PyErr) -> Self {
        ModelInterfaceError::Error(err.to_string())
    }
}

impl From<ModelInterfaceError> for PyErr {
    fn from(err: ModelInterfaceError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}
