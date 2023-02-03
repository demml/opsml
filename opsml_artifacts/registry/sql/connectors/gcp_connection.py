import os
from enum import Enum
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import root_validator
from typing import cast, Dict, Any
from opsml_artifacts.registry.sql.connectors.base_connection import BaseSQLConnection
from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter, GCPSecretManager, GCPClient, GcpCreds
import logging

logger = logging.getLogger(__name__)


ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC


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


class GcpSecretVarGetter:
    def __init__(self, gcp_credentials: GcpCreds):
        self.gcp_creds = gcp_credentials
        client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=self.gcp_creds.creds,
        )
        self.secret_client = cast(GCPSecretManager, client)

    def get_secret(self, secret_name: str) -> str:
        return self.secret_client.get_secret(
            project_name=self.gcp_creds.project,
            secret=secret_name,
        )


class CloudSQLConnection(BaseSQLConnection):
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
        db_type (str): database type. Either "mysql" or "postgres"

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
    db_type: str = os.getenv("ARTIFACT_DB_TYPE")
    load_from_secrets: bool = False

    @root_validator(pre=True)
    def get_env_vars(cls, env_vars):  # pylint: disable=no-self-argument)
        creds = GcpCredsSetter().get_creds()
        env_vars["gcp_creds"] = creds.creds
        env_vars["path"] = os.getcwd()

        # replace gcsfs with gcs
        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        env_vars["gcsfs_creds"] = creds.creds.with_scopes([scopes])

        if bool(env_vars.get("load_from_secrets")):
            env_vars = cls.load_vars_from_gcp(env_vars=env_vars, gcp_credentials=creds)

        return env_vars

    @classmethod
    def load_vars_from_gcp(cls, env_vars: Dict[str, Any], gcp_credentials: GcpCreds):
        secret_getter = GcpSecretVarGetter(gcp_credentials=gcp_credentials)
        logger.info("Loading environment variables")

        for name, value in {i.name.lower(): i.value for i in GcpVariables}.items():
            env_vars[name] = secret_getter.get_secret(secret_name=value)

        return env_vars

    def _set_connection_name(self):
        return f"{self.gcp_project}:{self.gcp_region}:{self.db_instance_name}"

    def _set_db_type(self):
        if self.db_type == "mysql":
            return "pymysql"

        return "pg8000"

    def _get_conn(self):

        db_type = self._set_db_type()
        connection_name = self._set_connection_name()

        with Connector(ip_type=ip_type, credentials=self.gcp_creds) as connector:
            conn = connector.connect(
                connection_name,
                db_type,
                user=self.db_username,
                password=self.db_password,
                db=self.db_name,
            )

            return conn

    def _set_sqlalchemy_url(self):
        if self.db_type == "mysql":
            return "mysql+pymysql://"
        return "postgresql+pg8000://"

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        url = self._set_sqlalchemy_url()
        engine = sqlalchemy.create_engine(url, creator=self._get_conn)
        return engine
