from ast import Raise
from re import S
from .data_model import DataModel, SqlDataRegistrySchema, base
from opsml_data.helpers.utils import GCPCredentials
from opsml_data.helpers.defaults import defaults
from .data_formatter import DataFormatter
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import os
import sqlalchemy
from sqlalchemy import select, desc
import pandas as pd
import numpy as np
from typing import Union, Dict, Any
from pyshipt_logging.logger import ShiptLogging

logger = ShiptLogging.get_default_logger()


class TableRegistry:
    @staticmethod
    def get_schema(table_name: str):
        for table_schema in base.__subclasses__():
            if table_name == table_schema.__tablename__:
                return table_schema

        # return default
        return SqlDataRegistrySchema


class GCPSqlConnector:
    def __init__(
        self,
        instance_name: str,
        db_name: str,
        username: str,
        password: str,
        gcp_project: str = defaults.GCP_PROJECT,
        gcp_region: str = defaults.GCP_REGION,
    ):
        self._instance_connection_name = f"{gcp_project}:{gcp_region}:{instance_name}"
        self._db_name = db_name
        self._username = username
        self._password = password

        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
        creds = GCPCredentials(gcp_creds=defaults.GCP_CREDS)

        self.connector = self._set_connector(
            ip_type=ip_type,
            creds=creds,
        )

    def _set_connector(self, ip_type, creds: GCPCredentials):
        return Connector(
            ip_type=ip_type,
            credentials=creds.credentials,
        )

    def _sql_conn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(
            self._instance_connection_name,
            "pymysql",
            user=self._username,
            password=self._password,
            db=self._db_name,
        )

        return conn

    def create_sql_engine(self) -> sqlalchemy.engine.base.Engine:
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=self._sql_conn,
        )
        logger.info("Connected to db")
        return engine


class SqlRegistry:
    def __init__(
        self,
        schema: sqlalchemy.Table,
        db_name: str,
        engine: sqlalchemy.engine.base.Engine,
    ):

        self.engine = engine
        self.schema = schema
        self.schema.__table_args__ = {"schema": f"{db_name}"}

    def submit_query(self, query):
        with self.engine.connect() as db_conn:
            results = db_conn.execute(query)

            return results

    def insert(self, data: Dict[str, Any]):

        self.submit_query(
            self.schema.__table__.insert(data),
        )

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

    def write_to_registry(
        self,
        data: Union[pd.DataFrame, np.array],
        table_name: str,
        user_email: str,
    ):

        max_version = self.max_table_version(
            table_name=table_name,
        )
        data = DataFormatter.convert_data_to_arrow(data)
        feature_map = DataFormatter.create_table_schema(data)

        # save data to gcs

        model = DataModel(**data)

        # convert data
        data = DataFormatter.convert_data_to_arrow(data)
        schema = DataFormatter.get_schema(data)

        # check if table exists in registry

        # write to gcs

        # DataModel(table_name=table_name, feature_mapping=schema)
