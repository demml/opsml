use crate::cli::arg::ScouterArgs;
use crate::error::CliError;
use opsml_registry::registries::card::OpsmlCardRegistry;
use opsml_types::RegistryType;
use pyo3::prelude::*;
use scouter_client::ProfileStatusRequest;

/// Update the drift profile status
///
/// # Arguments
/// * `args` - The command line arguments
///
///
#[pyfunction]
pub fn update_drift_profile_status(args: &ScouterArgs) -> Result<(), CliError> {
    let request = ProfileStatusRequest {
        space: args.space.clone(),
        name: args.name.clone(),
        version: args.version.clone(),
        active: args.active,
        drift_type: Some(args.drift_type.clone()),
        deactivate_others: args.deactivate_others,
    };

    let client = OpsmlCardRegistry::new(RegistryType::Model)?;

    client.update_drift_profile_status(&request)?;
    Ok(())
}
