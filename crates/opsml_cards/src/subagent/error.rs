use thiserror::Error;

#[derive(Error, Debug)]
pub enum SubAgentError {
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

impl From<toml::ser::Error> for SubAgentError {
    fn from(err: toml::ser::Error) -> Self {
        SubAgentError::TomlError(err.to_string())
    }
}

impl From<SubAgentError> for crate::error::CardError {
    fn from(err: SubAgentError) -> Self {
        crate::error::CardError::Error(err.to_string())
    }
}

impl From<opsml_agent_cli::FrameworkError> for SubAgentError {
    fn from(e: opsml_agent_cli::FrameworkError) -> Self {
        SubAgentError::Error(e.to_string())
    }
}
