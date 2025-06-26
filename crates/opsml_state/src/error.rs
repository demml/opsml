use thiserror::Error;

#[derive(Error, Debug)]
pub enum StateError {
    #[error("Failed to create runtime: {0}")]
    RuntimeError(#[source] std::io::Error),

    #[error("Failed to read tools: {0}")]
    ReadToolsError(String),

    #[error("Failed to read config: {0}")]
    ReadConfigError(String),

    #[error("Failed to read mode: {0}")]
    ReadModeError(String),

    #[error("Failed to write tools: {0}")]
    WriteToolsError(String),

    #[error("Failed to write config: {0}")]
    WriteConfigError(String),

    #[error("Failed to write mode")]
    WriteModeError,

    #[error("Failed to get storage settings")]
    GetStorageSettingsError,
}
