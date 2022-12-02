from opsml_data.connector.base import GCPQueryRunner
from opsml_data.helpers.utils import GCSStorageClient
from opsml_data.connector.snowflake import SnowflakeDataGetter
from opsml_data.helpers.defaults import params
import pandas
from unittest.mock import patch


def test_submit_query(mock_response):

    with patch.object(GCPQueryRunner, "_post") as _post:
        _post.return_value = mock_response
        query_runner = GCPQueryRunner(
            snowflake_api_auth=params.snowflake_api_auth,
            snowflake_api_url=params.snowflake_api_url,
        )

        response = query_runner.submit_query(
            query="test",
        )

        assert "gs" in response.gcs_url


def test_snowflake_to_dataframe(mock_response, gcs_url):

    with patch.object(GCPQueryRunner, "_post") as _post:
        _post.return_value = mock_response

        with patch.object(GCSStorageClient, "delete_object") as delete_object:
            delete_object.return_value = False

            data_getter = SnowflakeDataGetter()

            # get data
            df = data_getter._gcs_to_dataframe(gcs_url)
            assert type(df) == pandas.DataFrame
