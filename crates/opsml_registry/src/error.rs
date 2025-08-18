use anyhow::Error as AnyhowError;
use opsml_cards::error::CardError;
use opsml_client::error::RegistryError as ApiRegistryError;
use opsml_settings::error::SettingsError;
use opsml_state::error::StateError;
use opsml_storage::storage::error::StorageError;
use opsml_types::error::TypeError;
use opsml_types::RegistryType;
use opsml_utils::error::{PyUtilError, UtilError};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum RegistryError {
    #[error(transparent)]
    ScouterClientError(#[from] scouter_client::ClientError),

    #[error(transparent)]
    SettingsError(#[from] SettingsError),

    #[error(transparent)]
    StateError(#[from] StateError),

    #[error("Server feature not enabled")]
    ServerFeatureNotEnabled,

    #[error("Service not supported")]
    ServiceNotSupported,

    #[error(transparent)]
    VersionError(#[from] opsml_semver::error::VersionError),

    #[error(transparent)]
    ApiRegistryError(#[from] ApiRegistryError),

    #[error(transparent)]
    SerdeQsError(#[from] serde_qs::Error),

    #[error(transparent)]
    JoinError(#[from] tokio::task::JoinError),

    #[error(transparent)]
    PyErr(#[from] pyo3::PyErr),

    #[error(transparent)]
    TypeError(#[from] TypeError),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    PyUtilError(#[from] PyUtilError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    CardError(#[from] CardError),

    #[error(transparent)]
    CryptError(#[from] opsml_crypt::error::CryptError),

    #[error(transparent)]
    StorageError(#[from] StorageError),

    #[error("At least one of uid, name, space, version must be provided")]
    MissingArgsError,

    #[error("Failed to set attribute: {0}")]
    FailedToSetAttributeError(&'static str),

    #[error("Card type {0} not supported")]
    CardTypeNotSupported(RegistryType),

    #[error("Registry type {0} not supported")]
    RegistryTypeNotSupported(RegistryType),

    #[error("Invalid card type: {0}")]
    InvalidCardType(String),

    #[error("{0}")]
    CustomError(String),

    #[error("Datacard does not exist in the registry")]
    DataCardNotExistError,

    #[error("Failed to get cards from service")]
    FailedToGetCardsFromService,

    #[error("Failed to extract cards from service")]
    FailedToExtractCardsFromService,

    #[error("Card registry type does not match registry type")]
    RegistryTypeMismatchError,

    #[error("Failed to update service card")]
    UpdateServiceCardError,

    #[error("Card is not a valid card")]
    NotValidCardError,

    #[error(transparent)]
    AnyhowError(#[from] AnyhowError),

    #[cfg(feature = "server")]
    #[error(transparent)]
    SqlError(#[from] opsml_sql::error::SqlError),

    #[error("Failed to downcast")]
    DowncastError(String),

    #[error("Failed to create scouter client")]
    CreateClientError,

    #[error("ScouterClient not found")]
    ScouterClientNotFoundError,

    #[error(transparent)]
    SerdeJsonError(#[from] serde_json::Error),

    #[error("Request failed: {0}")]
    RequestError(#[from] reqwest::Error),

    #[error(transparent)]
    OpsmlApiClientError(#[from] opsml_client::error::ApiClientError),

    #[error("AsyncOpsmlRegistry only supports client mode")]
    AsyncOpsmlRegistryOnlySupportsClientMode,
}

impl From<RegistryError> for PyErr {
    fn from(err: RegistryError) -> PyErr {
        let msg = err.to_string();
        error!("{}", msg);
        PyRuntimeError::new_err(msg)
    }
}

impl<'a> From<pyo3::DowncastError<'a, 'a>> for RegistryError {
    fn from(err: pyo3::DowncastError) -> Self {
        RegistryError::DowncastError(err.to_string())
    }
}
