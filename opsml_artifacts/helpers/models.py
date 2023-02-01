from datetime import datetime
from enum import Enum

from google.oauth2.service_account import Credentials
from pydantic import BaseModel, BaseSettings


class SnowflakeParams(BaseModel):
    """Loads snowflake credentials from gcs"""

    username: str
    password: str
    host: str
    database: str
    warehouse: str
    role: str


class Settings(BaseSettings):
    gcp_project: str
    gcs_bucket: str
    gcp_region: str
    app_env: str
    path: str
    gcp_creds: Credentials
    snowflake_api_auth: str
    snowflake_api_url: str
    db_username: str
    db_password: str
    db_name: str
    db_instance_name: str
    gcsfs_creds: Credentials
    run_id: str = str(datetime.now().strftime("%Y%m%d%H%M%S"))

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


class GcpVariables(str, Enum):
    APP_ENV = "app_env"
    GCS_BUCKET = "gcs_bucket"
    GCP_REGION = "gcp_region"
    GCP_PROJECT = "gcp_project"
    SNOWFLAKE_API_AUTH = "snowflake_api_auth"
    SNOWFLAKE_API_URL = "snowflake_api_url"
    DB_NAME = "artifact_registry_db_name"
    DB_INSTANCE_NAME = "artifact_registry_instance_name"
    DB_USERNAME = "artifact_registry_username"
    DB_PASSWORD = "artifact_registry_password"
    GCP_ARTIFACT_REGISTRY = "ml_container_registry"
    NETWORK = "ml_network"
    PIPELINE_SCHEDULER_URI = "ml_pipeline_scheduler_uri"


class GcpCreds(BaseModel):
    creds: Credentials
    project: str

    class Config:
        arbitrary_types_allowed = True
