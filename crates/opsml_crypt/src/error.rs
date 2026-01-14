use opsml_utils::error::UtilError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CryptError {
    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error("Failed to encrypt file: {0}")]
    EncryptError(String),

    #[error("Failed to decrypt file: {0}")]
    DecryptError(String),

    #[error(transparent)]
    UtilError(#[from] UtilError),

    #[error("Failed to derive key: {0}")]
    DeriveKeyError(String),

    #[error("Failed to generate salt")]
    GenerateSaltError,

    #[error("Failed to create AES-256-GCM key: {0}")]
    AesCreateError(String),

    #[error("Failed to encrypt key using AES-256-GCM")]
    EncryptKeyError,

    #[error("Failed to decrypt key using AES-256-GCM")]
    DecryptKeyError,
}
