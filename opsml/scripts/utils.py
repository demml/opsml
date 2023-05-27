import os
from enum import Enum
from opsml.helpers.request_helpers import ApiClient

TRACKING_URI = os.environ.get("OPSML_TRACKING_URI")


# this is a duplicate of opsml/registry/sql/sql_schema
# This is done in order to avoid instantiating DefaultSettings when using CLI
class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    RUN = os.getenv("ML_RUN_REGISTRY_NAME", "OPSML_RUN_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")
    PROJECT = os.getenv("ML_PROJECT_REGISTRY_NAME", "OPSML_PROJECT_REGISTRY")


def get_api_client() -> ApiClient:
    return ApiClient(base_url=TRACKING_URI)
