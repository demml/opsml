from typing import List, Optional

from opsml.extras.installer_base import Installer
from opsml.extras.types import IntegrationType
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

BASE_GCP_REQUIREMENTS = [
    "gcsfs>=2022.11.0,<2023.0.0",
    "google-auth==1.35.0",
    "google-cloud-scheduler>=2.0.0,<=3.0.0",
    "google-cloud-storage>=2.2.1,<3.0.0",
]


class GcpInstaller(Installer):
    """Google dependencies for OPSML"""

    @property
    def packages(self) -> List[str]:
        return BASE_GCP_REQUIREMENTS

    @staticmethod
    def validate(integration_type: str) -> bool:
        return integration_type == IntegrationType.GCP


class VertexInstaller(Installer):
    """Google dependencies for OPSML"""

    @property
    def packages(self) -> List[str]:
        return [
            *BASE_GCP_REQUIREMENTS,
            "google-cloud-pipeline-components>=1.0.41,<=2.0.0",
            "kfp>=1.8.19,<2.0.0",
        ]

    @staticmethod
    def validate(integration_type: str) -> bool:
        return integration_type == IntegrationType.VERTEX


class KubeFlowInstaller(Installer):
    """Google dependencies for OPSML"""

    @property
    def packages(self) -> List[str]:
        return ["kfp>=1.8.19,<2.0.0"]

    @staticmethod
    def validate(integration_type: str) -> bool:
        return integration_type == IntegrationType.KUBEFLOW


def get_installer(integration_type: str, install_type: str) -> Optional[Installer]:
    """
    Gets the correct integration installer and installs necessary packages
    Args:
        integration_type:
            Type of integration (GCP, Vertex, KubeFlow)
        install_type:
            Type of installer to use (pip or poetry)
    """
    installer = next(
        (
            installer
            for installer in Installer.__subclasses__()
            if installer.validate(integration_type=integration_type)
        ),
        None,
    )

    if installer is None:
        logger.info("No integration class found. Nothing to install")
        return None

    return installer(install_type=install_type)
