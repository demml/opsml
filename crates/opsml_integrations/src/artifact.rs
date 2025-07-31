use opsml_cards::error::CardError;
use opsml_cards::utils::BaseArgs;
use opsml_cards::Card;
use opsml_registry::base::OpsmlRegistry;
use opsml_registry::error::RegistryError;
use opsml_registry::registry;
use opsml_storage::storage_client;
use opsml_types::contracts::{ArtifactKey, CardQueryArgs};
use opsml_types::RegistryType;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error(transparent)]
    CardError(#[from] CardError),
    #[error(transparent)]
    RegistryError(#[from] RegistryError),

    #[error("Either space + name or uid must be provided")]
    InvalidArguments,

    #[error("{0}")]
    RunTimeError(String),
}

impl From<ServiceError> for PyErr {
    fn from(err: ServiceError) -> PyErr {
        let msg = err.to_string();
        PyRuntimeError::new_err(msg)
    }
}

impl From<PyErr> for ServiceError {
    fn from(err: PyErr) -> ServiceError {
        ServiceError::RunTimeError(err.to_string())
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct OpsmlArtifactService {
    key: ArtifactKey,
}

// given x, we need to get the Artifact Key

#[pymethods]
impl OpsmlArtifactService {
    #[new]
    #[pyo3(signature = (space=None, name=None, version=None, uid=None))]
    fn new(
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
    ) -> Result<Self, ServiceError> {
        // if name + space is None, and uid is None, then we return an error
        let has_space_name = space.is_some() && name.is_some();
        let has_uid = uid.is_some();
        if !has_space_name && !has_uid {
            return Err(ServiceError::InvalidArguments);
        }

        let registry = OpsmlRegistry::new(RegistryType::Service)?;

        let args = CardQueryArgs {
            space: space.map(|s| s.to_string()),
            name: name.map(|n| n.to_string()),
            version: version.map(|v| v.to_string()),
            uid: uid.map(|u| u.to_string()),
            registry_type: RegistryType::Service,
            ..Default::default()
        };

        let key = registry.get_key(&args)?;

        Ok(OpsmlArtifactService { key })
    }
}
