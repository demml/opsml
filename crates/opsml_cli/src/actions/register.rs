use crate::actions::lock::lock_service_card;
use crate::error::CliError;
use opsml_service::ServiceSpec;
use pyo3::prelude::*;
use std::path::PathBuf;
use tracing::debug;

/// Will create an `opsml.lock` file based on the service configuration specified within the opsmlspec.yaml file.
#[pyfunction]
pub fn register_service(path: PathBuf) -> Result<(), CliError> {
    debug!("Registering service with path: {:?}", path);
    // handle case of no cards
    let spec = ServiceSpec::from_path(&path)?;

    //Register the service
    lock_service_card(&spec, spec.space(), &spec.name)?;

    Ok(())
}
