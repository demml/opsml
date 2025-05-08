use azure_core::error::Error as AzureCoreError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AzureError {
    #[error(transparent)]
    CoreError(#[from] AzureCoreError),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    ReqwestError(#[from] reqwest::Error),

    #[error(transparent)]
    VarError(#[from] std::env::VarError),

    #[error("Invalid parts type for Azure storage")]
    InvalidPartsTypeError,
}
