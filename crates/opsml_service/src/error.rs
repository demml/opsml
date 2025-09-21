use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("Drift configuration is only valid for model cards")]
    InvalidConfiguration,
}
