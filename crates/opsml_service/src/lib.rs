pub mod error;
pub mod service;

pub use service::{
    Card, DeploymentConfig, DriftConfig, GpuConfig, McpCapability, McpTransport, Metadata,
    Resources, ServiceConfig, ServiceSpec, ServiceType,
};
