use opsml_registry::download::download_service;
use opsml_service::{service::SpaceConfig, ServiceSpec};
use opsml_types::contracts::{
    DeploymentConfig, GpuConfig, McpCapability, McpConfig, McpTransport, Resources, ServiceConfig,
    ServiceMetadata, ServiceType,
};
use pyo3::prelude::*;

pub fn add_service_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(download_service, m)?)?;
    m.add_class::<ServiceType>()?;
    m.add_class::<ServiceSpec>()?;
    m.add_class::<SpaceConfig>()?;
    m.add_class::<ServiceMetadata>()?;
    m.add_class::<ServiceConfig>()?;
    m.add_class::<DeploymentConfig>()?;
    m.add_class::<Resources>()?;
    m.add_class::<GpuConfig>()?;
    m.add_class::<McpConfig>()?;
    m.add_class::<McpTransport>()?;
    m.add_class::<McpCapability>()?;

    Ok(())
}
