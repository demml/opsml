use crate::cli::arg::ScouterArgs;
use crate::error::CliError;
use opsml_registry::base::OpsmlRegistry;
use pyo3::prelude::*;
use scouter_client::{DriftType, ProfileStatusRequest};

pub fn update_drift_profile_status(args: &ScouterArgs) -> Result<(), CliError> {
    let prequest = ProfileStatusRequest {
        space: args.space.clone(),
        name: args.name.clone(),
        version: args.version.clone(),
        active: args.active,
        drift_type: Some(DriftType::from(args.drift_type.clone())),
    };
    Ok(())
}
