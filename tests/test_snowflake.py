import time

import pandas as pd

from opsml_data.connector.snowflake import SnowflakeQueryRunner


# remove these once networking is configured
def test_snowflake_query(test_query):

    runner = SnowflakeQueryRunner()
    response, query_id = runner.submit_query(query=test_query)

    assert response.status_code == 200

    response = runner.query_status(query_id=query_id)
    finished = False
    while not finished:
        response = runner.query_status(
            query_id=query_id,
        )

        status = response.json()["query_status"]

        if status.lower() == "success":
            break

        if "error" in status.lower():
            message = response.json()["message"]
            raise ValueError(message)

        time.sleep(2)


def test_snowflake_query_df(test_query):

    runner = SnowflakeQueryRunner()
    df = runner.query_to_dataframe(query=test_query)
    assert isinstance(df, pd.DataFrame)

    runner = SnowflakeQueryRunner(on_vpn=True)
    df = runner.query_to_dataframe(query=test_query)
    assert isinstance(df, pd.DataFrame)


def test_snowflake_file_df():

    runner = SnowflakeQueryRunner()
    df = runner.query_to_dataframe(sql_file="test_sql.sql")
    assert isinstance(df, pd.DataFrame)
