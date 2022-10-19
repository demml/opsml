from ast import Raise
from re import S
from .data_model import DataModel, SqlDataRegistrySchema, base
from .data_formatter import DataFormatter
from sqlalchemy import select, desc
import sqlalchemy
import pandas as pd
import numpy as np
from typing import Union, Dict, Any


class TableRegistry:
    @staticmethod
    def get_schema(table_name: str):
        for table_schema in base.__subclasses__():
            if table_name == table_schema.__tablename__:
                return table_schema

        # return default
        return SqlDataRegistrySchema


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

    def write_to_registry(self, data: Union[pd.DataFrame, np.array], table_name: str):

        # convert data
        data = DataFormatter.convert_data_to_arrow(data)
        schema = DataFormatter.get_schema(data)

        # check if table exists in registry

        # write to gcs

        # DataModel(table_name=table_name, feature_mapping=schema)
