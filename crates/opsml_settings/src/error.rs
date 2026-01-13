use base64::DecodeError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SettingsError {
    #[error("Failed to decode base64: {0}")]
    Base64DecodeError(#[from] DecodeError),
}
