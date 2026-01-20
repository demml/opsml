use thiserror::Error;

#[derive(Error, Debug)]
pub enum ApiClientError {
    #[error("Failed to create headers for opsml client")]
    CreateHeaderError(#[from] reqwest::header::InvalidHeaderValue),

    #[error("Failed to create opsml client: {0}")]
    CreateClientError(#[source] reqwest::Error),

    #[error("Request failed: {0}")]
    RequestError(#[from] reqwest::Error),

    #[error("Unauthorized")]
    Unauthorized,

    #[error("Failed to update auth token")]
    UpdateAuthError,

    #[error("Forbidden: {0}")]
    ForbiddenError(String),

    #[error("Permission denied: {0}")]
    PermissionDeniedError(String),

    #[error(transparent)]
    SerdeQsError(#[from] serde_qs::Error),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error("{0}")]
    ServerError(String),
}

#[derive(Error, Debug)]
pub enum RegistryError {
    #[error(transparent)]
    SerdeQsError(#[from] serde_qs::Error),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    ApiClientError(#[from] ApiClientError),

    #[error("Request failed: {0}")]
    RequestError(#[from] reqwest::Error),

    #[error("Failed to get create card")]
    CreateCardError,

    #[error("Failed to get update card")]
    UpdateCardError,

    #[error("Failed to get delete card")]
    DeleteCardError,

    #[error("Failed to insert hardware metrics")]
    InsertHardwareMetricError,

    #[error("Failed to insert metrics")]
    InsertMetricError,

    #[error("Failed to insert parameters")]
    InsertParameterError,
}
