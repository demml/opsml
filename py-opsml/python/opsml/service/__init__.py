# mypy: disable-error-code="attr-defined"
# python/opsml/card/__init__.py
from .._opsml import (
    DeploymentConfig,
    GpuConfig,
    McpCapability,
    McpConfig,
    McpTransport,
    Resources,
    ServiceConfig,
    ServiceMetadata,
    ServiceSpec,
    ServiceType,
    SpaceConfig,
    download_service,
)

__all__ = [
    "ServiceSpec",
    "ServiceType",
    "SpaceConfig",
    "ServiceMetadata",
    "ServiceConfig",
    "DeploymentConfig",
    "Resources",
    "GpuConfig",
    "McpConfig",
    "McpTransport",
    "McpCapability",
    "download_service",
]
