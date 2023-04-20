from enum import Enum


class IntegrationType(str, Enum):
    VERTEX = "vertex"
    KUBEFLOW = "kubeflow"
    GCP = "gcp"


class InstallType(str, Enum):
    POETRY = "poetry"
    PIP = "pip"
