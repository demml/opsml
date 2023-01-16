import os
import tempfile
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from pyshipt.helpers.connection_string import ConnectionString, DBType
from pyshipt.helpers.database import SnowflakeDatabase
from pyshipt.helpers.model import ColumnType, Table
from pyshipt.helpers.pandas import PandasHelper as ph
from pyshipt_logging import ShiptLogging

from opsml_artifacts.analysis.models import AnalysisAttributes, PayDataFrame
from opsml_artifacts.connector.snowflake import SnowflakeQueryRunner
from opsml_artifacts.helpers.gcp_utils import GCSStorageClient
from opsml_artifacts.helpers.settings import SnowflakeCredentials, settings
from opsml_artifacts.helpers.utils import FindPath

from ..helpers import exceptions

logger = ShiptLogging.get_logger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))


@dataclass
class SqlArgs:
    metro_level: bool
    outlier_removal: bool
    metro: str = ""
    metro_group: str = ""
    outlier_flg: str = ""

    def __post_init__(self):
        if self.metro_level:
            self.metro = "METRO,"
            self.metro_group = "GROUP BY METRO"

        if self.outlier_removal:
            self.outlier_flg = "AND EVAL_OUTLIER = 0"


# this code needs to be refactored (do it once networking is figured out)


class FlightPlanSQL:
    def __init__(self, analysis_attributes: AnalysisAttributes):
        self.attributes = analysis_attributes
        self.filename = f"{self.attributes.analysis_level}_{self.attributes.analysis_type}_analysis.sql"
        self.sql_args = SqlArgs(
            metro_level=self.attributes.metro_level,
            outlier_removal=self.attributes.outlier_removal,
        )

    def open_sql_file(self) -> str:
        sql_path = FindPath().find_filepath(self.filename, dir_path)

        with open(sql_path, "r", encoding="utf-8") as sql:
            sql_string = sql.read()
        return sql_string

    def format_sql(self, sql_string: str) -> str:
        """Analyzer specific formatting"""
        raise NotImplementedError

    def get_sql(self):
        sql_string = self.open_sql_file()
        return self.format_sql(sql_string=sql_string)

    @staticmethod
    def validate(analysis_type: str) -> bool:
        """Used for validating analysis type"""
        raise NotImplementedError


class PaySQL(FlightPlanSQL):
    def format_sql(self, sql_string: str) -> str:

        sql_string = sql_string.format(
            prediction_table=self.attributes.table_name,
            metro=self.sql_args.metro,
            metro_group=self.sql_args.metro_group,
            outlier_flg=self.sql_args.outlier_flg,
        )

        return sql_string

    @staticmethod
    def validate(analysis_type: str) -> bool:
        return analysis_type.lower() == "pay"


class ErrorSQL(FlightPlanSQL):
    def format_sql(self, sql_string: str) -> str:

        sql_string = sql_string.format(
            prediction_table=self.attributes.table_name,
            metro=self.sql_args.metro,
            metro_group=self.sql_args.metro_group,
        )

        return sql_string

    @staticmethod
    def validate(analysis_type: str) -> bool:
        return analysis_type.lower() == "error"


class ComputeClient:
    def __init__(self) -> None:
        """Instantiates base compute client for analysis"""
        pass

    @staticmethod
    def validate(compute_env: str) -> bool:
        """Validate compute env"""
        raise NotImplementedError

    def create_analysis_dataframe(
        self,
        prediction_dataframe: pd.DataFrame,
        table_name: str,
        query: str,
    ) -> pd.DataFrame:
        raise NotImplementedError()


class GcpComputeClient(ComputeClient):
    def __init__(self) -> None:
        self.data_getter = SnowflakeQueryRunner()
        self.storage_client = GCSStorageClient(gcp_credentials=settings.gcp_creds)

    def upload_dataframe_to_gcs(
        self,
        dataframe: pd.DataFrame,
        table_name: str,
    ) -> str:
        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            filename = f"{table_name}.csv"
            dataframe.to_csv(f"{tmpdirname}/{filename}", index=False)

            gcs_uri = self.storage_client.upload(
                gcs_bucket=settings.gcs_bucket,
                filename=f"{tmpdirname}/{filename}",
                destination_path=f"data/{filename}",
            )

        return gcs_uri

    def gcs_to_table(
        self,
        gcs_uri: str,
        table_name: str,
    ):

        status, reason = self.data_getter._gcs_to_table(  # pylint: disable=protected-access
            gcs_url=gcs_uri, table_name=table_name
        )

        if status.lower() != "succeeded":
            logger.error("Failed to create snowflake table for %s: %s", table_name, reason)
            raise exceptions.SnowFlakeApiError(reason)

        return status

    def get_dataframe_from_query(self, table_name: str, gcs_uri: str, query: str):
        dataframe = self.data_getter.query_to_dataframe(query=query)
        self.storage_client.delete_object_from_url(gcs_uri=gcs_uri)
        self.data_getter.submit_query(query=f"DROP TABLE DATA_SCIENCE.{table_name}")

        return dataframe

    def create_analysis_dataframe(
        self,
        prediction_dataframe: pd.DataFrame,
        table_name: str,
        query: str,
    ) -> pd.DataFrame:
        gcs_uri = self.upload_dataframe_to_gcs(
            dataframe=prediction_dataframe,
            table_name=table_name,
        )

        self.gcs_to_table(
            gcs_uri=gcs_uri,
            table_name=table_name,
        )
        dataframe = self.get_dataframe_from_query(
            table_name=table_name,
            gcs_uri=gcs_uri,
            query=query,
        )

        return dataframe

    @staticmethod
    def validate(compute_env: str) -> bool:
        return compute_env.lower() == "gcp"


class LocalComputeClient(ComputeClient):
    def __init__(self) -> None:
        sf_kwargs = SnowflakeCredentials.credentials()

        query = {
            "warehouse": [sf_kwargs.warehouse],
            "role": [sf_kwargs.role],
        }

        conn_str = ConnectionString(
            dbtype=DBType.SNOWFLAKE,
            username=sf_kwargs.username,
            password=sf_kwargs.password,
            host=sf_kwargs.host,
            port=None,
            dbname=sf_kwargs.database,
            query=query,
        )
        self.database = SnowflakeDatabase(conn_str)

    def get_table_schema(self, id_col: str):
        model = Table(
            {
                id_col: ColumnType.Text,
                "checkout_time": ColumnType.Float,
                "delivery_time": ColumnType.Float,
                "pick_time": ColumnType.Float,
                "drop_time": ColumnType.Float,
                "drive_time": ColumnType.Float,
                "wait_time": ColumnType.Float,
            }
        )

        return model

    def get_id_col(self, prediction_dataframe: pd.DataFrame):
        return prediction_dataframe.filter(like="id").columns[0]

    def create_analysis_dataframe(
        self,
        prediction_dataframe: pd.DataFrame,
        table_name: str,
        query: str,
    ) -> pd.DataFrame:
        id_col = self.get_id_col(prediction_dataframe=prediction_dataframe)
        model = self.get_table_schema(id_col=id_col)
        ph.dataframe_to_table(
            dataframe=prediction_dataframe,
            model=model,
            schema="data_science",
            table=table_name,
            database=self.database,
            temp_dir="/tmp",
        )

        with self.database.get_connection() as cnxn, cnxn.cursor() as cursor:
            cursor.execute(query)
            dataframe = cursor.fetch_pandas_all()
            cursor.execute(
                f"DROP TABLE data_science.{table_name}",
            )

        return dataframe

    @staticmethod
    def validate(compute_env: str) -> bool:
        return compute_env.lower() == "local"


class PayErrorAnalyzer:
    def __init__(
        self,
        prediction_dataframe: pd.DataFrame,
        analysis_attributes: AnalysisAttributes,
    ):
        self.attributes = analysis_attributes
        self.sql_getter = self.set_sql(analysis_attributes=analysis_attributes)
        self.compute_client = self.set_compute_client(analysis_attributes=analysis_attributes)
        self.analysis_data = PayDataFrame(prediction_dataframe).get_valid_data()

    def set_compute_client(self, analysis_attributes: AnalysisAttributes):

        compute_client = next(
            compute_client
            for compute_client in ComputeClient.__subclasses__()
            if compute_client.validate(
                compute_env=analysis_attributes.compute_env,
            )
        )
        return compute_client()

    def set_sql(self, analysis_attributes: AnalysisAttributes):

        sql = next(
            sql
            for sql in FlightPlanSQL.__subclasses__()
            if sql.validate(analysis_type=analysis_attributes.analysis_type)
        )
        return sql(analysis_attributes=analysis_attributes)

    def append_predictions_to_dataframe(
        self,
        dataframe: pd.DataFrame,
        labels: List[str],
    ):
        # check each prediction type
        for preds, label in zip(
            [
                self.analysis_data.ids,
                self.analysis_data.checkout_predictions,
                self.analysis_data.delivery_predictions,
                self.analysis_data.pick_predictions,
                self.analysis_data.drop_predictions,
                self.analysis_data.drive_predictions,
                self.analysis_data.wait_predictions,
            ],
            labels,
        ):
            if preds is not None:
                dataframe[label] = preds
        return dataframe

    def create_pred_dataframe(self):

        columns = [
            self.attributes.id_col,
            "checkout_time",
            "delivery_time",
            "pick_time",
            "drop_time",
            "drive_time",
            "wait_time",
        ]

        analysis_df = pd.DataFrame(
            np.empty((len(self.analysis_data.ids), 7)) * np.nan,
            columns=columns,
        )
        # check each prediction type
        analysis_df = self.append_predictions_to_dataframe(
            dataframe=analysis_df,
            labels=columns,
        )

        return analysis_df

    def run_analysis(
        self,
    ) -> pd.DataFrame:

        # Create dataframe
        analysis_df = self.create_pred_dataframe()
        query = self.sql_getter.get_sql()
        dataframe = self.compute_client.create_analysis_dataframe(
            table_name=self.attributes.table_name,
            prediction_dataframe=analysis_df,
            query=query,
        )

        return dataframe
