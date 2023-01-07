import os

import pymysql
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from pyshipt_logging.logger import ShiptLogging

from opsml_data.helpers.settings import settings

logger = ShiptLogging.get_default_logger()

ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC


class SqlConnection:
    def __init__(self):

        self._instance_connection_name = f"{settings.gcp_project}:{settings.gcp_region}:{settings.db_instance_name}"

    def get_conn(self) -> pymysql.connections.Connection:

        with Connector(ip_type=ip_type, credentials=settings.gcp_creds) as connector:
            conn = connector.connect(
                self._instance_connection_name,
                "pymysql",
                user=settings.db_username,
                password=settings.db_password,
                db=settings.db_name,
            )

            return conn


def create_sql_engine() -> sqlalchemy.engine.base.Engine:
    engine = sqlalchemy.create_engine("mysql+pymysql://", creator=SqlConnection().get_conn)
    return engine
