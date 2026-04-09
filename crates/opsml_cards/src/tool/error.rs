use thiserror::Error;

#[derive(Error, Debug)]
pub enum ToolError {
    #[error("{0}")]
    Error(String),

    #[error(transparent)]
    SerdeError(#[from] serde_json::Error),

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    SerdeYamlError(#[from] serde_yaml::Error),

    #[error(transparent)]
    UtilError(#[from] opsml_utils::error::UtilError),

    #[error("TOML serialization error: {0}")]
    TomlError(String),
}

impl From<ToolError> for crate::error::CardError {
    fn from(err: ToolError) -> Self {
        crate::error::CardError::Error(err.to_string())
    }
}

impl From<opsml_agent_cli::FrameworkError> for ToolError {
    fn from(e: opsml_agent_cli::FrameworkError) -> Self {
        ToolError::Error(e.to_string())
    }
}

impl From<toml::ser::Error> for ToolError {
    fn from(err: toml::ser::Error) -> Self {
        ToolError::TomlError(err.to_string())
    }
}

impl From<toml::de::Error> for ToolError {
    fn from(err: toml::de::Error) -> Self {
        ToolError::TomlError(err.to_string())
    }
}
