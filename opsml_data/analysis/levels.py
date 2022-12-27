import os
import tempfile
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from pyshipt.helpers.database_helper import ShiptDB
from pyshipt.helpers.model import ColumnType, Table
from pyshipt.helpers.pandas import PandasHelper as ph
from pyshipt_logging import ShiptLogging

from opsml_data.connector.snowflake import SnowflakeQueryRunner
from opsml_data.helpers.settings import settings

from ..helpers import exceptions
from ..helpers.settings import SnowflakeCredentials
from ..helpers.utils import FindPath, GCSStorageClient

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
class LevelHandler:
    def __init__(
        self,
        id_col: str,
        compute_env: str,
    ):
        self.id_col = id_col
        self.compute_env = compute_env

        if compute_env == "gcp":
            self.data_getter = SnowflakeQueryRunner()
            self.storage_client = GCSStorageClient(gcp_credentials=settings.gcp_creds)

        else:
            sf_kwargs = SnowflakeCredentials.credentials()
            self.database = ShiptDB.warehouse(
                username=sf_kwargs.username,
                password=sf_kwargs.password,
                host=sf_kwargs.host,
                warehouse=sf_kwargs.warehouse,
                role=sf_kwargs.role,
            )

    def _get_sql_template(
        self,
        analysis_level: str,
        analysis_type: str,
        table_name: str,
        metro_level: bool,
        outlier_removal: bool,
    ):

        filename = f"{analysis_level}_{analysis_type}_analysis.sql"
        sql_path = FindPath().find_filepath(
            filename,
            dir_path,
        )

        with open(sql_path, "r", encoding="utf-8") as sql:
            sql_string = sql.read()

        sql_args = SqlArgs(
            metro_level=metro_level,
            outlier_removal=outlier_removal,
        )

        if analysis_type == "pay":
            sql_string = sql_string.format(
                prediction_table=table_name,
                metro=sql_args.metro,
                metro_group=sql_args.metro_group,
                outlier_flg=sql_args.outlier_flg,
            )

        else:
            sql_string = sql_string.format(
                prediction_table=table_name,
                metro=sql_args.metro,
                metro_group=sql_args.metro_group,
            )

        return sql_string

    def _create_pred_dataframe(
        self,
        ids: List[str],
        checkout_predictions: List[float] = None,
        delivery_predictions: List[float] = None,
        pick_predictions: List[float] = None,
        drop_predictions: List[float] = None,
        drive_predictions: List[float] = None,
        wait_predictions: List[float] = None,
        id_col: str = None,
    ):

        columns = [
            id_col.upper(),
            "CHECKOUT_TIME",
            "DELIVERY_TIME",
            "PICK_TIME",
            "DROP_TIME",
            "DRIVE_TIME",
            "WAIT_TIME",
        ]

        analysis_df = pd.DataFrame(
            np.empty((len(ids), 7)) * np.nan,
            columns=columns,
        )

        # check each prediction type
        for preds, label in zip(
            [
                ids,
                checkout_predictions,
                delivery_predictions,
                pick_predictions,
                drop_predictions,
                drive_predictions,
                wait_predictions,
            ],
            columns,
        ):
            if preds is not None:
                analysis_df[label] = preds

        return analysis_df

    def _upload_dataframe_to_gcs(
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

    def _gcs_to_table(
        self,
        gcs_url: str,
        table_name: str,
    ):

        status, reason = self.data_getter._gcs_to_table(  # pylint: disable=protected-access
            gcs_url=gcs_url,
            table_name=table_name,
        )

        if status.lower() != "succeeded":
            logger.error("Failed to create snowflake table for %s: %s", table_name, reason)
            raise exceptions.SnowFlakeApiError(reason)

        return status

    def _get_table_schema(self, id_col: str):
        model = Table(
            {
                id_col: ColumnType.String,
                "checkout_time": ColumnType.Float,
                "delivery_time": ColumnType.Float,
                "pick_time": ColumnType.Float,
                "drop_time": ColumnType.Float,
                "drive_time": ColumnType.Float,
                "wait_time": ColumnType.Float,
            }
        )

        return model

    def _run_analysis(
        self,
        ids: List[str],
        checkout_predictions: List[float] = None,
        delivery_predictions: List[float] = None,
        pick_predictions: List[float] = None,
        drop_predictions: List[float] = None,
        drive_predictions: List[float] = None,
        wait_predictions: List[float] = None,
        analysis_type: str = None,
        analysis_level: str = None,
        table_name: str = None,
        outlier_removal: bool = False,
        schema: str = None,
        metro_level: bool = False,
    ) -> pd.DataFrame:

        # Create dataframe
        analysis_df = self._create_pred_dataframe(
            ids,
            checkout_predictions=checkout_predictions,
            delivery_predictions=delivery_predictions,
            pick_predictions=pick_predictions,
            drop_predictions=drop_predictions,
            drive_predictions=drive_predictions,
            wait_predictions=wait_predictions,
            id_col=self.id_col,
        )

        # Get formatted sql query
        query = self._get_sql_template(
            analysis_level=analysis_level,
            analysis_type=analysis_type,
            table_name=table_name,
            metro_level=metro_level,
            outlier_removal=outlier_removal,
        )

        if self.compute_env == "gcp":
            gcs_uri = self._upload_dataframe_to_gcs(
                dataframe=analysis_df,
                table_name=table_name,
            )

            self._gcs_to_table(
                gcs_url=gcs_uri,
                table_name=table_name,
            )

            dataframe = self.data_getter.run_query(query=query)

            self.storage_client.delete_object_from_url(
                gcs_uri=gcs_uri,
            )

            self.data_getter.submit_query(query=f"DROP TABLE DATA_SCIENCE.{table_name}")
            return dataframe

        model = self._get_table_schema(self.id_col)
        ph.dataframe_to_table(
            dataframe=analysis_df,
            model=model,
            schema=schema,
            table=table_name,
            database=self.database,
            temp_dir="/tmp",
        )

        with self.database.get_connection() as cnxn, cnxn.cursor() as cursor:
            cursor.execute(query)
            dataframe = cursor.fetch_pandas_all()
            cursor.execute(
                f"DROP TABLE {schema}.{table_name}",
            )

        return dataframe


class Bundle(LevelHandler):
    def __init__(self, compute_env: str):
        self.id_col = "bundle_id"
        self.tabe_name = f"preds_bundle_{settings.run_id}"

        super().__init__(
            id_col=self.id_col,
            compute_env=compute_env,
        )

    def run_analysis(
        self,
        ids: List[str],
        checkout_predictions: List[float] = None,
        delivery_predictions: List[float] = None,
        pick_predictions: List[float] = None,
        drop_predictions: List[float] = None,
        drive_predictions: List[float] = None,
        wait_predictions: List[float] = None,
        analysis_type: str = None,
        outlier_removal: bool = None,
        metro_level: bool = False,
        schema: str = None,
    ):
        dataframe = self._run_analysis(
            ids=ids,
            checkout_predictions=checkout_predictions,
            delivery_predictions=delivery_predictions,
            pick_predictions=pick_predictions,
            drop_predictions=drop_predictions,
            drive_predictions=drive_predictions,
            wait_predictions=wait_predictions,
            table_name=self.tabe_name,
            analysis_level="bundle",
            analysis_type=analysis_type,
            outlier_removal=outlier_removal,
            metro_level=metro_level,
            schema=schema,
        )

        return dataframe

    @staticmethod
    def match_analysis_type(
        analysis_type: str,
    ):
        if analysis_type.lower() == "bundle":
            return True

        return False


class Order(LevelHandler):
    def __init__(self, compute_env: str):
        self.id_col = "ng_order_id"
        self.tabe_name = f"preds_order_{settings.run_id}"

        super().__init__(
            id_col=self.id_col,
            compute_env=compute_env,
        )

    def run_analysis(
        self,
        ids: List[str],
        checkout_predictions: List[float] = None,
        delivery_predictions: List[float] = None,
        pick_predictions: List[float] = None,
        drop_predictions: List[float] = None,
        drive_predictions: List[float] = None,
        wait_predictions: List[float] = None,
        analysis_type: str = None,
        outlier_removal: bool = None,
        metro_level: bool = False,
        schema: str = None,
    ) -> pd.DataFrame:
        dataframe = self._run_analysis(
            ids=ids,
            checkout_predictions=checkout_predictions,
            delivery_predictions=delivery_predictions,
            pick_predictions=pick_predictions,
            drop_predictions=drop_predictions,
            drive_predictions=drive_predictions,
            wait_predictions=wait_predictions,
            table_name=self.tabe_name,
            analysis_level="order",
            analysis_type=analysis_type,
            outlier_removal=outlier_removal,
            metro_level=metro_level,
            schema=schema,
        )
        return dataframe

    @staticmethod
    def match_analysis_type(
        analysis_type: str,
    ):
        return bool(analysis_type.lower() == "order")
