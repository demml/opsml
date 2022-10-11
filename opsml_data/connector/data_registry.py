from dataclasses import dataclass
from opsml_data.helpers.utils import GCPCredentials
from opsml_data.helpers.defaults import defaults
from opsml_data.connector.sql_registry import SqlRegistry
from google.cloud.sql.connector import Connector, IPTypes
from pyshipt_logging.logger import ShiptLogging
import pymysql
import os
import sqlalchemy

logger = ShiptLogging.get_default_logger()


class DataRegistry(SqlRegistry):
    def __init__(
        self,
        gcp_project: str,
        gcp_region: str,
        instance_name: str,
        db_name: str,
        username: str,
        password: str,
    ):

        self._instance_connection_name = f"{gcp_project}:{gcp_region}:{instance_name}"
        self._db_name = db_name
        self._username = username
        self._password = password

        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

        # composition components
        creds = GCPCredentials(gcp_creds=defaults.GCP_CREDS)

        self.connector = Connector(
            ip_type=ip_type,
            credentials=creds.credentials,
        )

        engine = self.get_sql_engine()

        super().__init__(
            db_name=self._db_name,
            engine=engine,
        )

    def get_conn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(
            self._instance_connection_name,
            "pymysql",
            user=self._username,
            password=self._password,
            db=self._db_name,
        )

        return conn

    def get_sql_engine(self) -> sqlalchemy.engine.base.Engine:
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=self.get_conn,
        )
        logger.info("Connected to db")
        return engine
