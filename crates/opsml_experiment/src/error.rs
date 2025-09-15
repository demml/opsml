use opsml_cards::error::CardError;
use opsml_crypt::error::CryptError;
use opsml_registry::error::RegistryError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::TypeError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum ExperimentError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error(transparent)]
    CryptError(#[from] CryptError),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error("Failed to load experiment card")]
    LoadCardError(#[source] RegistryError),

    #[error("Failed to insert metric")]
    InsertMetricError(#[source] RegistryError),

    #[error("Failed to insert parameter")]
    InsertParameterError(#[source] RegistryError),

    #[error("Failed to find artifact: {0}")]
    ArtifactNotFoundError(String),

    #[error("Path does not exist")]
    PathNotExistError,

    #[error("Path is not a file. Use log_artifacts if you wish to log multiple artifacts")]
    PathNotFileError,

    #[error(transparent)]
    WalkDirError(#[from] walkdir::Error),

    #[error(transparent)]
    StripPrefixError(#[from] std::path::StripPrefixError),

    #[error("Failed to convert OsString to String: {0:?}")]
    IntoStringError(std::ffi::OsString),

    #[error("Figure is not an image")]
    FigureIsNotImageError,

    #[error("Figure is not a matplotlib figure")]
    FigureIsNotMatplotlibError,

    #[error("Failed to downcast Python object: {0}")]
    DowncastError(String),

    #[error("Invalid parameter argument. Log_parameters accepts either a dictionary of parameters or a list of parameters. Received: {0}")]
    InvalidParametersArgument(String),

    #[error("{0}")]
    MissingImportError(String),

    #[error(transparent)]
    EvaluationError(#[from] opsml_evaluate::error::EvaluationError),
}

impl From<std::ffi::OsString> for ExperimentError {
    fn from(err: std::ffi::OsString) -> Self {
        ExperimentError::IntoStringError(err)
    }
}

impl From<ExperimentError> for PyErr {
    fn from(err: ExperimentError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for ExperimentError {
    fn from(err: pyo3::DowncastError) -> Self {
        ExperimentError::DowncastError(err.to_string())
    }
}
