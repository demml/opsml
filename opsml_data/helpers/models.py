from google.oauth2.service_account import Credentials
from pydantic import BaseModel, Extra, root_validator
import datetime


class Params(BaseModel):
    """Creates pipeline params associated
    with the current pipeline run.
    """

    gcp_project: str
    gcs_bucket: str
    gcp_region: str
    run_id: str
    app_env: str
    gcp_creds: Credentials
    snowflake_api_auth: str
    snowflake_api_url: str
    db_username: str
    db_password: str
    db_name: str
    db_instance_name: str
    gcsfs_creds = str

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def set_extras(cls, values):  # pylint: disable=no-self-argument
        """Pre checks"""

        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        values["gcsfs_creds"] = values["gcp_creds"].with_scopes([scopes])

        return values


class SnowflakeParams(BaseModel):
    """Loads snowflake credentials from gcs"""

    username: str
    password: str
    host: str
    database: str
    warehouse: str
    role: str
