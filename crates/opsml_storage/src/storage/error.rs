use opsml_state::error::StateError;
use opsml_utils::error::UtilError;
use thiserror::Error;
use tracing::error;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error(transparent)]
    StateError(#[from] StateError),
}
