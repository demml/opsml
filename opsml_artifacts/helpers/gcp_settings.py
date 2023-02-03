from datetime import datetime
import os
from enum import Enum
from pydantic import root_validator, BaseModel
from typing import cast, Dict
from google.oauth2.service_account import Credentials

from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter
import logging

logger = logging.getLogger(__name__)


class CloudSqlConnection:
    """Cloud SQL connection string to pass to the registry for establishing
    a connection to a MySql or Postgres DB

    Args:
        gcp_project (str): Project where the CloudSQL database resides
        gcs_bucket (str): Name or cloud storage bucket to use (this is where data will be stored)
        gcp_region (str): GCP Region associated with the CloudSQL instance
        db_instance_name (str): Instance name for CloudSQL database
        db_name (str): Database name
        db_username (str): Username for CloudSQL connection
        db_password (str): Password for CloudSql connection

    Returns:
        Instantiated class with required CloudSQL connection arguments
    """

    gcp_project: str = os.getenv("GCP_PROJECT")
    gcs_bucket: str = os.getenv("GCS_BUCKET")
    gcp_region: str = os.getenv("GCS_REGION")
    db_instance_name: str = os.getenv("ARTIFACT_DB_INSTANCE_NAME")
    db_username: str = os.getenv("ARTIFACT_DB_USERNAME")
    db_password: str = os.getenv("ARTIFACT_DB_PASSWORD")
    db_name: str = os.getenv("ARTIFACT_DB_NAME")

    class Config:
        arbitrary_types_allowed = True
        extra = "allowed"

    @root_validator(pre=True)
    def get_env_vars(cls, env_vars):  # pylint: disable=no-self-argument)
        creds = GcpCredsSetter().get_creds()
        env_vars["gcp_creds"] = creds.creds
        env_vars["path"] = os.getcwd()

        # replace gcsfs with gcs
        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        env_vars["gcsfs_creds"] = creds.creds.with_scopes([scopes])

        return env_vars
