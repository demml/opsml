use opsml_client::OpsmlApiClient;
use opsml_types::{RegistryMode, RegistryType};
use serde::Deserialize;
use std::sync::Arc;

#[derive(Debug, Deserialize)]
pub struct ErrorResponse {
    pub error: String,
}

pub trait Registry {
    fn client(&self) -> &Arc<OpsmlApiClient>;
    fn mode(&self) -> RegistryMode {
        RegistryMode::Client
    }
    fn table_name(&self) -> String;
    fn registry_type(&self) -> &RegistryType;
}
