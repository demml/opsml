use thiserror::Error;

#[derive(Error, Debug)]
pub enum PyProjectTomlError {
    #[error("Failed to find absolute path")]
    AbsolutePathError(#[source] std::io::Error),

    // Borrowed from UV
    #[error("No file name {0} in current directory or any parent directory")]
    MissingPyprojectToml(String),

    #[error("Failed to read `pyproject.toml`")]
    ReadError(#[source] std::io::Error),

    #[error("Failed to parse `pyproject.toml`")]
    ParseError(#[from] toml_edit::TomlError),

    #[error("Failed to get current directory")]
    CurrentDirError(#[source] std::io::Error),

    #[error("Failed to deserialize `pyproject.toml`")]
    TomlSchema(#[source] toml_edit::de::Error),

    #[error("Failed to deserialize `opsml.lock`")]
    LockFileSchema(#[source] toml_edit::de::Error),

    #[error("Failed to write opsml.lock file")]
    FailedToLockFile(#[source] std::io::Error),

    #[error("Failed to read opsml.lock file")]
    FailedToReadLockFile(#[source] std::io::Error),

    #[error("Failed to parse opsml.lock file")]
    FailedToParseLockFile(#[source] toml_edit::TomlError),

    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,
}
