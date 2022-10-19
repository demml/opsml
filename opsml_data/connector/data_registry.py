from ctypes import Union
from opsml_data.connector.sql_registry import (
    SqlRegistry,
    TableRegistry,
    GCPSqlConnector,
)
from opsml_data.connector.data_model import DataModel
from opsml_data.connector.data_formatter import DataFormatter
from opsml_data.helpers.utils import GCSStorageClient
from pyshipt_logging.logger import ShiptLogging
from sqlalchemy import select, desc
from typing import Dict, Any, Union
from opsml_data.helpers.defaults import defaults
import pandas as pd
import numpy as np

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
        self.storage_client = GCSStorageClient(gcs_bucket="opsml-data-registry")

        sql_connector = GCPSqlConnector(
            instance_name=instance_name,
            db_name=db_name,
            username=username,
            password=password,
            gcp_project=gcp_project,
            gcp_region=gcp_region,
        )

        engine = sql_connector.create_sql_engine()

        # Table schema
        table_schema = TableRegistry.get_schema(table_name)

        super().__init__(
            schema=table_schema,
            db_name=db_name,
            engine=engine,
        )

    def list_tables(self):
        sql_statement = select(self.schema.table_name).group_by(
            self.schema.table_name,
        )
        results = self.submit_query(sql_statement).fetchall()

        return [row.table_name for row in results]

    def add_data(
        self,
        table_name: str,
        user_email: str,
        data: Union[pd.DataFrame, np.array],
    ):
        """
        Adds new data record to data registry.

        Args:
            table_name: Name of table. If table name is same as an existing table,
            a new version will be created.
            user_email: Email associated with this data.
            data: A pandas dataframe or numpy array.
        """

        max_version = self.max_table_version(
            table_name=table_name,
        )
        data = DataFormatter.convert_data_to_arrow(data)
        feature_map = DataFormatter.create_table_schema(data)

        # save data to gcs

        model = DataModel(**data)

        # algo
        # Convert to data model
        # get max version of table
        # update version

        self.insert(model.dict())
