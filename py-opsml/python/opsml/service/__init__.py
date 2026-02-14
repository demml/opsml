# mypy: disable-error-code="attr-defined"
# python/opsml/card/__init__.py
from .._opsml import (
    DeploymentConfig,
    GpuConfig,
    McpCapability,
    McpConfig,
    McpTransport,
    OpsmlServiceSpec,
    Resources,
    ServiceConfig,
    ServiceMetadata,
    ServiceType,
    SpaceConfig,
    download_service,
)

__all__ = [
    "OpsmlServiceSpec",
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
