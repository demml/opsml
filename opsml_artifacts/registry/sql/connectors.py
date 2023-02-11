# pylint: disable=[import-outside-toplevel,import-outside-toplevel]

import os
from typing import Any, Dict, Optional, Tuple, Type, Union
from enum import Enum

import sqlalchemy
from pydantic import BaseModel, Field, root_validator

from opsml_artifacts.helpers.settings import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class CloudSqlType(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"


class PythonCloudSqlType(str, Enum):
    MYSQL = "pymysql"
    POSTGRES = "pg8000"


class BaseSQLConnection(BaseModel):
    """Base Connection model that all connections inherit from"""

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    def _set_sqlalchemy_url(self):
        raise NotImplementedError

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        raise NotImplementedError

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        raise NotImplementedError


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
        db_type (str): database type. Either "mysql" or "postgres". Default is "mysql"
        iam_auth (bool): Whether to use IAM auth when connecting to the DB. Only applicable for Postgres
        storage_backend (str): Which storage system to use. Defaults to GCP

    Returns:
        Instantiated class with required CloudSQL connection arguments
    """

    gcp_project: str = Field(..., env="OPSML_GCP_PROJECT")
    gcs_bucket: str = Field(..., env="OPSML_GCS_BUCKET")
    gcp_region: str = Field(..., env="OPSML_GCS_REGION")
    db_instance_name: str = Field(..., env="OPSML_DB_INSTANCE_NAME")
    db_username: str = Field(..., env="OPSML_DB_USERNAME")
    db_password: Optional[str] = Field(..., env="OPSML_DB_PASSWORD")
    db_name: str = Field(..., env="OPSML_DB_NAME")
    db_type: str = Field(CloudSqlType.MYSQL.value, env="OPSML_DB_TYPE")
    storage_backend: str = "gcp"
    load_from_secrets: bool = False
    iam_auth: bool = True

    @root_validator(pre=True)
    def get_env_vars(cls, env_vars):  # pylint: disable=no-self-argument)
        creds, env_vars = cls.set_gcp_creds(env_vars=env_vars)

        if env_vars.get("load_from_secrets"):
            logger.info("Loading environment variables")
            env_vars = cls.load_vars_from_gcp(env_vars=env_vars, gcp_credentials=creds)

        return env_vars

    @classmethod
    def set_gcp_creds(cls, env_vars: Dict[str, Any]):

        from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter

        creds = GcpCredsSetter().get_creds()
        env_vars["gcp_creds"] = creds.creds
        env_vars["path"] = os.getcwd()

        # try removing this (dont want to do this long term- limit permissions)
        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        env_vars["gcsfs_creds"] = creds.creds.with_scopes([scopes])

        return creds, env_vars

    @classmethod
    def load_vars_from_gcp(cls, env_vars: Dict[str, Any], gcp_credentials):

        """Loads GCP vars from SecretManager

        env_vars (Dict): Dictionary of attributes passed to pydantic model
        """
        from opsml_artifacts.helpers.gcp_utils import GcpSecretVarGetter, GcpVariables

        secret_getter = GcpSecretVarGetter(gcp_credentials=gcp_credentials)
        for name, value in {i.name.lower(): i.value for i in GcpVariables}.items():
            env_vars[name] = secret_getter.get_secret(secret_name=value)

        return env_vars

    def _get_ip_type(self) -> str:
        from google.cloud.sql.connector import IPTypes

        return IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    def _get_connection_name(self) -> str:
        return f"{self.gcp_project}:{self.gcp_region}:{self.db_instance_name}"

    def _get_python_db_type(self) -> str:
        if self.db_type == CloudSqlType.MYSQL:
            return PythonCloudSqlType.MYSQL.value
        return PythonCloudSqlType.POSTGRES.value

    def _get_conn_defaults(self) -> Tuple[str, str, str]:

        ip_type = self._get_ip_type()
        db_type = self._get_db_type()
        connection_name = self._get_connection_name()

        return ip_type, db_type, connection_name

    def _mysql_conn(self, connector: Any, connection_name: str, db_type: str):

        return connector.connect(
            connection_name,
            db_type,
            user=self.db_username,
            db=self.db_name,
        )

    def _get_conn_type(self, connection_name: str, db_type: str) -> Tuple[str, bool]:
        """Sets the appropriate CloudSQL Args based on DB type.
        Defaults to IAM auth for Postgres
        """

        connection_args = {
            "instance_connection_string": connection_name,
            "driver": db_type,
            "db": self.db_name,
            "user": self.db_username,
        }

        if db_type == CloudSqlType.MYSQL or not self.iam_auth:
            connection_args["password"] = self.db_password
            return connection_args

        connection_args["enable_iam_auth"] = True
        return connection_args

    def _get_conn(self):

        """Creates the mysql or postgres CloudSQL client"""
        from google.cloud.sql.connector import Connector

        ip_type, db_type, connection_name = self._get_conn_defaults()
        connection_args = self._get_conn_type(
            db_type=db_type,
            connection_name=connection_name,
        )

        with Connector(ip_type=ip_type, credentials=self.gcp_creds) as connector:  # pylint: disable=no-member
            conn = connector.connect(**connection_args)
            return conn

    def _set_sqlalchemy_url(self):
        """Sets sqalchemy url depending on type of CloudSQL db"""

        if self.db_type == CloudSqlType.MYSQL:
            return "mysql+pymysql://"
        return "postgresql+pg8000://"

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        """Creates SQLAlchemy engine"""
        url = self._set_sqlalchemy_url()
        engine = sqlalchemy.create_engine(url, creator=self._get_conn)
        return engine

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == "gcp"


class LocalSQLConnection(BaseSQLConnection):
    """Connection string to pass to the registry for establishing
    a connection to a SQLite database

    Args:
        db_file_path (str): Optional file path to sqlite database, If no path is provided, a
        new database named "opsml_artifacts.db" will be created in the home user directory.
        If the "opsml_artifacts.db" already exists, a connection will be re-established (the
        database will not be overwritten)
        storage_backend (str): Which storage system to use. Defaults to local
    Returns:
        Instantiated class with required SQLite arguments
    """

    db_file_path: str = f"{os.path.expanduser('~')}/opsml_artifacts_database.db"
    storage_backend: str = "local"

    def _set_sqlalchemy_url(self):
        return "sqlite://"

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        url = self._set_sqlalchemy_url()
        execution_options = {"schema_translate_map": {"ds-artifact-registry": None}}
        engine = sqlalchemy.create_engine(f"{url}/{self.db_file_path}", execution_options=execution_options)
        return engine

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == "local"


SqlConnectorType = Union[CloudSQLConnection, LocalSQLConnection]


class SQLConnector:
    """Interface for finding correct subclass of BaseSQLConnection"""

    @staticmethod
    def get_connector(connector_type: Optional[str] = None) -> Type[BaseSQLConnection]:
        """Gets the appropriate SQL connector given the type specified"""

        if connector_type is None:
            conn_type = "local"
        conn_type = str(connector_type).lower()

        connector = next(
            (
                connector
                for connector in BaseSQLConnection.__subclasses__()
                if connector.validate_type(connector_type=conn_type)
            ),
            LocalSQLConnection,
        )
        return connector


# future implementation
# class SnowflakeConnection(BaseSQLConnection):
# class BigqueryConnection(BaseSQLConnection):
