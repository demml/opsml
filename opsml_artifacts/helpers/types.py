from enum import Enum


class OpsmlUri(str, Enum):
    STORAGE_URI = "OPSML_STORAGE_URI"
    TRACKING_URI = "OPSML_TRACKING_URI"
    RUN_ID = "OPSML_RUN_ID"


class OpsmlAuth(str, Enum):
    USERNAME = "OPSML_USERNAME"
    PASSWORD = "OPSML_PASSWORD"
