import time

import pandas as pd

from opsml_artifacts.connector.snowflake import SnowflakeQueryRunner


# remove these once networking is configured
def test_snowflake_query(test_query, mock_snowflake_query_runner):

    runner = SnowflakeQueryRunner()
    response, query_id = runner.submit_query(query=test_query)
    assert response == 200

    finished = False
    while not finished:
        response = runner.query_status(
            query_id=query_id,
        )

        status = response["query_status"]

        if status.lower() == "success":
            break


def test_snowflake_query_df(test_query, mock_snowflake_query_runner):

    runner = SnowflakeQueryRunner()
    df = runner.query_to_dataframe(query=test_query)
    assert isinstance(df, pd.DataFrame)

    runner = SnowflakeQueryRunner(on_vpn=True)
    df = runner.query_to_dataframe(query=test_query)
    assert isinstance(df, pd.DataFrame)


def test_snowflake_file_df(mock_snowflake_query_runner):

    runner = SnowflakeQueryRunner()
    df = runner.query_to_dataframe(sql_file="test_sql.sql")
    assert isinstance(df, pd.DataFrame)
