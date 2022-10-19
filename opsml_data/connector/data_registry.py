from opsml_data.helpers.utils import GCPCredentials
from opsml_data.helpers.defaults import defaults
from opsml_data.connector.sql_registry import SqlRegistry, TableRegistry
from opsml_data.connector.data_model import DataModel
from google.cloud.sql.connector import Connector, IPTypes
from pyshipt_logging.logger import ShiptLogging
import pymysql
import os
import sqlalchemy
from sqlalchemy import select, desc
from typing import Dict, Any

logger = ShiptLogging.get_default_logger()


class DataRegistry(SqlRegistry):
    def __init__(
        self,
        instance_name: str,
        db_name: str,
        username: str,
        password: str,
        table_name: str = defaults.REGISTRY_TABLE,
        gcp_project: str = defaults.GCP_PROJECT,
        gcp_region: str = defaults.GCP_REGION,
        gcp_bucket: str = defaults.GCS_BUCKET,
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

        # create engine
        engine = self._create_sql_engine()

        # Table schema
        schema = TableRegistry.get_schema(table_name)

        super().__init__(
            schema=schema,
            db_name=self._db_name,
            engine=engine,
        )

    def _set_conn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(
            self._instance_connection_name,
            "pymysql",
            user=self._username,
            password=self._password,
            db=self._db_name,
        )

        return conn

    def _create_sql_engine(self) -> sqlalchemy.engine.base.Engine:
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=self._set_conn,
        )
        logger.info("Connected to db")
        return engine

    def list_tables(self):
        sql_statement = select(self.schema.table_name).group_by(
            self.schema.table_name,
        )
        results = self.submit_query(sql_statement).fetchall()

        return [row.table_name for row in results]

    def max_table_version(self, table_name: str):
        sql_statement = (
            select(self.schema.version)
            .where(self.schema.table_name == table_name)
            .order_by(desc(self.schema.version))
            .limit(1)
        )

        result = self.submit_query(sql_statement).scalar()

        if result is None:
            return 0

        return result

    def _insert_data(self, data: Dict[str, Any]):

        model = DataModel(**data)
        self.insert(model.dict())
