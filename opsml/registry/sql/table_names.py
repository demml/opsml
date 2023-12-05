import os
from enum import Enum, unique


@unique
class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    RUN = os.getenv("ML_RUN_REGISTRY_NAME", "OPSML_RUN_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")
    PROJECT = os.getenv("ML_PROJECT_REGISTRY_NAME", "OPSML_PROJECT_REGISTRY")
    AUDIT = os.getenv("ML_AUDIT_REGISTRY_NAME", "OPSML_AUDIT_REGISTRY")

    @staticmethod
    def from_str(name: str) -> "RegistryTableNames":
        l_name = name.strip().lower()
        if l_name == "data":
            return RegistryTableNames.DATA
        if l_name == "model":
            return RegistryTableNames.MODEL
        if l_name == "run":
            return RegistryTableNames.RUN
        if l_name == "pipeline":
            return RegistryTableNames.PIPELINE
        if l_name == "project":
            return RegistryTableNames.PROJECT
        if l_name == "audit":
            return RegistryTableNames.AUDIT
        raise NotImplementedError()
