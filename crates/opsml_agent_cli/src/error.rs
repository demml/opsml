#[derive(Debug, thiserror::Error)]
pub enum FrameworkError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    Json(#[from] serde_json::Error),

    #[error(transparent)]
    Yaml(#[from] serde_yaml::Error),

    #[error("TOML serialization error: {0}")]
    TomlError(String),

    #[error("corrupt config at '{0}': JSON parse failed — refusing to overwrite with empty config")]
    CorruptConfig(String),

    #[error("cannot determine home directory; global install requires $HOME to be set")]
    NoHomeDir,
}

impl From<toml::ser::Error> for FrameworkError {
    fn from(e: toml::ser::Error) -> Self {
        Self::TomlError(e.to_string())
    }
}
