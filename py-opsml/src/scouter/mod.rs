pub mod alert;
pub mod client;
pub mod drift;
pub mod observe;
pub mod profile;
pub mod queue;
pub mod tracing;
pub mod transport;
pub mod types;

use pyo3::prelude::*;

pub fn add_scouter_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    queue::add_queue_module(m)?;
    client::add_client_module(m)?;
    drift::add_drift_module(m)?;
    alert::add_alert_module(m)?;
    types::add_types_module(m)?;
    profile::add_profile_module(m)?;
    observe::add_observe_module(m)?;
    transport::add_transport_module(m)?;
    tracing::add_tracing_module(m)?;

    Ok(())
}
