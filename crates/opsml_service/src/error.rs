use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,

    #[error(transparent)]
    IoError(#[from] std::io::Error),

    #[error(transparent)]
    YamlError(#[from] serde_yaml::Error),
}
