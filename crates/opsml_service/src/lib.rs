pub mod error;
pub mod service;

pub use service::{
    Card, DeploymentConfig, DriftConfig, GpuConfig, Metadata, Resources, ServiceConfig,
    ServiceSpec, ServiceType,
};
