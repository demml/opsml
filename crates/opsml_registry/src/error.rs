use opsml_client::error::{ApiClientError, RegistryError as ApiRegistryError};
use opsml_settings::error::SettingsError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum RegistryError {
    #[error(transparent)]
    SettingsError(#[from] SettingsError),

    #[error("Server feature not enabled")]
    ServerFeatureNotEnabled,

    #[error(transparent)]
    ApiRegistryError(#[from] ApiRegistryError),
}
