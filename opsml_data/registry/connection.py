from google.cloud.sql.connector import Connector, IPTypes
import pymysql
from opsml_data.helpers.defaults import params
import os
from pyshipt_logging.logger import ShiptLogging
import sqlalchemy

logger = ShiptLogging.get_default_logger()

ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC


class SqlConnector:
    def __init__(self):

        self._instance_connection_name = f"{params.gcp_project}:{params.gcp_region}:{params.db_instance_name}"

    def get_conn(self) -> pymysql.connections.Connection:

        with Connector(ip_type=ip_type, credentials=params.gcp_creds) as connector:
            conn = connector.connect(
                self._instance_connection_name,
                "pymysql",
                user=params.db_username,
                password=params.db_password,
                db=params.db_name,
            )

            return conn


def create_sql_engine() -> sqlalchemy.engine.base.Engine:
    engine = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=SqlConnector().get_conn,
    )
    logger.info("Connected to db")
    return engine
