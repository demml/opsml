from enum import Enum

from google.oauth2.service_account import Credentials
from pydantic import BaseModel


class DBVars(BaseModel):
    db_name: str
    db_instance_name: str
    db_username: str
    db_password: str


testing_db_vars = DBVars(
    db_name="artifact_registry_db_name_testing",
    db_instance_name="artifact_registry_instance_name_testing",
    db_username="artifact_registry_username_testing",
    db_password="artifact_registry_password_testing",
)

non_testing_db_vars = DBVars(
    db_name="artifact_registry_db_name",
    db_instance_name="artifact_registry_instance_name",
    db_username="artifact_registry_username",
    db_password="artifact_registry_password",
)


class DBSecrets(BaseModel):
    testing: DBVars
    non_testing: DBVars

    class Config:
        arbitrary_types_allowed = True


class GcpVariables(str, Enum):
    APP_ENV = "app_env"
    GCS_BUCKET = "gcs_bucket"
    GCP_REGION = "gcp_region"
    GCP_PROJECT = "gcp_project"
    SNOWFLAKE_API_AUTH = "snowflake_api_auth"
    SNOWFLAKE_API_URL = "snowflake_api_url"


class GcpCreds(BaseModel):
    creds: Credentials
    project: str

    class Config:
        arbitrary_types_allowed = True


# create db secrets
db_secrets = DBSecrets(
    testing=testing_db_vars,
    non_testing=non_testing_db_vars,
)
