import time

import gcsfs
import pandas as pd
import pyarrow.parquet as pq
from pyshipt_logging import ShiptLogging

from opsml_data.connector.base import GcsFilePath, QueryRunner
from opsml_data.helpers.defaults import params

logger = ShiptLogging.get_logger(__name__)

file_sys = gcsfs.GCSFileSystem(
    project=params.gcp_project,
)


class SnowflakeQueryRunner(QueryRunner):
    def __init__(self):

        headers = {
            "Accept": "application/json",
            "Authorization": params.snowflake_api_auth,
        }

        super().__init__(
            api_prefix=params.snowflake_api_url,
            status_suffix="/v2/query_status",
            submit_suffix="/v2/async_query",
            results_suffix="/v2/query_results",
            headers=headers,
        )

    def run_query(
        self,
        query: str = None,
        sql_file: str = None,
    ) -> pd.DataFrame:

        """Submits a query to run

        Args:
            query (str): Optional query to run
            sql_file (str): Optional sql file to run

        Returns:
            Pandas dataframe
        """

        # submit
        response = self.submit_query(query=query, sql_file=sql_file)
        query_id = response.json()["query_id"]

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
