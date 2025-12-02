# mypy: disable-error-code="attr-defined"
# python/opsml/card/__init__.py
from .._opsml import (
    download_service,
    ServiceSpec,
    ServiceType,
    SpaceConfig,
    ServiceMetadata,
    ServiceConfig,
    DeploymentConfig,
    Resources,
    GpuConfig,
    McpConfig,
    McpTransport,
    McpCapability,
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
