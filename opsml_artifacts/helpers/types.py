from enum import Enum
from typing import cast
from google.oauth2.service_account import Credentials
from pydantic import BaseModel
import os


class GcpVariables(str, Enum):
    APP_ENV = "app_env"
    GCS_BUCKET = "gcs_bucket"
    GCP_REGION = "gcp_region"
    GCP_PROJECT = "gcp_project"
    SNOWFLAKE_API_AUTH = "snowflake_api_auth"
    SNOWFLAKE_API_URL = "snowflake_api_url"
    DB_NAME = ("artifact_registry_db_name",)
    DB_INSTANCE_NAME = ("artifact_registry_instance_name",)
    DB_USERNAME = ("artifact_registry_username",)
    DB_PASSWORD = ("artifact_registry_password",)


class GcpCreds(BaseModel):
    creds: Credentials
    project: str

    class Config:
        arbitrary_types_allowed = True
