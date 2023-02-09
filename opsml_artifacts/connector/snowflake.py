# pylint: disable=no-member
# this file will eventually be removed

import time
from typing import Optional

import gcsfs
import pandas as pd
import pyarrow.parquet as pq
from pyshipt_logging import ShiptLogging
from pyshipt_sql.connection_string import ConnectionString, DBType
from pyshipt_sql.engine import SnowflakeEngine

from opsml_artifacts.connector.base import GcsFilePath, QueryRunner
from opsml_artifacts.connector.settings import SnowflakeCredentials

logger = ShiptLogging.get_logger(__name__)


credentials = SnowflakeCredentials.credentials()
file_sys = gcsfs.GCSFileSystem(project=credentials.gcp_project)  # type: ignore


# Remove entire module once networking is figured out for vertex
# Pyshipt-sql should be used for sql connections


class SnowflakeQueryRunner(QueryRunner):
    def __init__(self, on_vpn: bool = False):

        self.on_vpn = on_vpn
        self.local_db = self._set_local_database()

        headers = {
            "Accept": "application/json",
            "Authorization": credentials.api_auth,
        }
        super().__init__(
            api_prefix=credentials.api_url,
            status_suffix="/v2/query_status",
            submit_suffix="/v2/async_query",
            results_suffix="/v2/query_results",
            headers=headers,
        )

    def _set_local_database(self):
        if self.on_vpn:
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
            return SnowflakeEngine(conn_str)
        return None

    @property
    def has_local_db(self):
        return bool(self.local_db)

    def run_local_query(self, sql: str) -> pd.DataFrame:
        with self.local_db.get_connection() as cnxn, cnxn.cursor() as cursor:
            cursor.execute(sql)
            dataframe = cursor.fetch_pandas_all()

        return dataframe

    def query_to_dataframe(
        self,
        query: Optional[str] = None,
        sql_file: Optional[str] = None,
    ) -> pd.DataFrame:

        """Submits a query to run

        Args:
            query (str): Optional query to run
            sql_file (str): Optional sql file to run

        Returns:
            Pandas dataframe
        """
        sql = self.load_sql(query=query, sql_file=sql_file)

        if self.has_local_db:
            try:
                dataframe = self.run_local_query(sql=sql)
                return dataframe

            except Exception as error:  # pylint: disable=broad-except
                logger.error("""Failed to connect to snowlake. Using API instead. %s""", error)

        # submit
        _, query_id = self.submit_query(query=sql)

        # poll
        self.poll_results(query_id=query_id)

        # get results (stream to gcs)
        gcs_metadata: GcsFilePath = self.results_to_gcs(query_id=query_id)
        dataframe = self.gcs_to_parquet(gcs_metadata=gcs_metadata)

        return dataframe

    def gcs_to_parquet(self, gcs_metadata: GcsFilePath):

        files = [
            "gs://" + path
            for path in file_sys.ls(
                path=gcs_metadata.gcs_bucket,
                prefix=gcs_metadata.gcs_filepath,
            )
        ]

        dataframe = (
            pq.ParquetDataset(
                path_or_paths=files,
                filesystem=file_sys,
            )
            .read()
            .to_pandas()
        )

        file_sys.rm(
            path=gcs_metadata.full_path,
            recursive=True,
        )

        return dataframe

    def results_to_gcs(self, query_id: str) -> GcsFilePath:
        response = self.query_results(
            query_id=query_id,
        )

        url = response.json()["gcs_url"]
        bucket = url.split("/")[2]
        file_path = "/".join(url.split("/")[3:])

        metadata = GcsFilePath(
            gcs_url=url,
            gcs_bucket=bucket,
            gcs_filepath=file_path,
        )

        return metadata

    def _gcs_to_table(
        self,
        gcs_url: str,
        table_name: str,
    ):

        data = {"url": gcs_url, "table_name": table_name}

        response = self._post_request(
            suffix="v2/csv_to_table",
            data=data,
        )

        response = response.json()
        return response["status"], response["reason"]

    def poll_results(self, query_id: str):
        # poll
        finished = False
        while not finished:
            response = self.query_status(
                query_id=query_id,
            )
            status = response.json()["query_status"]

            if status.lower() == "success":
                break

            if "error" in status.lower():
                message = response.json()["message"]
                logger.info("Query failed: %s", message)
                raise ValueError(message)

            time.sleep(2)
