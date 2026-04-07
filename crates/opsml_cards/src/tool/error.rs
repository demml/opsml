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
}

impl From<ToolError> for crate::error::CardError {
    fn from(err: ToolError) -> Self {
        crate::error::CardError::Error(err.to_string())
    }
}
