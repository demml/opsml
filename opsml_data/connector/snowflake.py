import pandas as pd
from pyshipt_logging import ShiptLogging

from opsml_data.connector.base import GCPQueryRunner
from opsml_data.helpers.defaults import params
from opsml_data.helpers.utils import FindPath, GCSStorageClient

logger = ShiptLogging.get_logger(__name__)


class SnowflakeDataGetter:
    """Takes a sql query, submits it to snowflake and
    returns a dataframe. Note - This class is only to
    be used when running jobs in vertex. In order to
    connect to Snowflake, queries submitted in vertex
    are first routed to an api that has been white listed
    to communicate with Snowflake. If you are running
    on local or in an env that has Snowflake access then
    use pyshipt.

    Args:
        gcs_bucket: GCS bucket to write to as an intermediary.
    """

    def __init__(
        self,
    ):
        self.query_runner = GCPQueryRunner(
            snowflake_api_auth=params.snowflake_api_auth,
            snowflake_api_url=params.snowflake_api_url,
        )

    def _gcs_to_dataframe(self, gcs_uri: str) -> pd.DataFrame:

        client = GCSStorageClient(gcp_credentials=params.gcp_creds)
        filename = client.download_object_from_uri(gcs_uri=gcs_uri)

        data = pd.read_csv(filename)

        # delete after converting to pandas
        client.delete_object_from_url(gcs_uri=gcs_uri)

        return data

    def _find_sql_file(self, sql_file_name: str) -> str:

        if sql_file_name is not None:
            sql_path = FindPath.find_filepath(
                sql_file_name,
            )

            # get query
            with open(sql_path, "r", encoding="utf-8") as sql:
                query = sql.read()

        return query

    def get_data(
        self,
        query: str = None,
        sql_file_name: str = None,
    ) -> pd.DataFrame:

        if sql_file_name is not None:
            query = self._find_sql_file(
                sql_file_name,
            )

        if query is None:
            msg = "No query provided in either args"  # noqa
            logger.error(msg)
            raise ValueError(msg)

        response = self.query_runner.submit_query(
            query=query,
        )

        data = self._gcs_to_dataframe(gcs_uri=response.gcs_url)

        return data
