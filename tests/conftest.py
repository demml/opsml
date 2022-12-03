import pytest
from opsml_data.helpers.defaults import params
import os
from pathlib import Path
from opsml_data.helpers.utils import FindPath
import pandas as pd
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    try:
        os.remove("gcp_key.json")
    except Exception as e:
        pass

    paths = [path for path in Path(os.getcwd()).rglob("*.csv")]
    for path in paths:
        if "pick_time_example.csv" in path.name:
            pass
        else:
            os.remove(path)


@pytest.fixture(scope="session")
def test_defaults():

    return params


@pytest.fixture(scope="session")
def mock_response():
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data = {
        "query_id": None,
        "gcs_url": "gs://py-opsml/data/e8e13de0e2a74f56be89d285fa97aab9.csv",
    }
    response = MockResponse(json_data=data, status_code=200)

    return response


@pytest.fixture(scope="session")
def gcs_url():
    return "gs://py-opsml/data/20220927155229.csv"


@pytest.fixture(scope="session")
def pick_predictions():
    csv_path = FindPath().find_filepath(
        "pick_time_example.csv",
        dir_path,
    )
    df = pd.read_csv(csv_path)
    return df["NG_ORDER_ID"].to_list(), df["PREDICTIONS"].to_list()


@pytest.fixture(scope="session")
def unique_id():
    id_ = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    return id_


@pytest.fixture(scope="session")
def sf_schema():
    return "data_science"


@pytest.fixture(scope="session")
def df_columns():
    return [
        "ng_order_id",
        "checkout_time",
        "delivery_time",
        "pick_time",
        "drop_time",
        "drive_time",
        "wait_time",
    ]


@pytest.fixture(scope="session")
def bundle_query():
    query = """
        SELECT
        TIME_BUNDLE_ID,
        DROP_OFF_TIME/60 AS ACTUAL,
        (NBR_ADDRESSES*3.8531) -0.0415 AS DROP_TIME
        FROM DATA_SCIENCE.OPSML_FP_BUNDLES_TIME_ACTUALS
        WHERE DROP_OFF_EVAL_FLG = 1
        AND DROP_OFF_EVAL_OUTLIER = 0
        """
    return query


@pytest.fixture(scope="session")
def order_query():
    query = """
        SELECT 
        NG_ORDER_ID,
        (3.8531) -0.0415 AS DROP_TIME,
        NULL AS CHECKOUT_TIME,
        NULL AS DELIVERY_TIME,
        NULL AS DRIVE_TIME,
        NULL AS WAIT_TIME,
        NULL AS PICK_TIME
        FROM DATA_SCIENCE.OPSML_FP_ORDERS_TIME_ACTUALS
        WHERE BUNDLE_TYPE = 'TARP'
        AND DROP_OFF_EVAL_FLG = 1
        AND DROP_OFF_EVAL_OUTLIER = 0
        """
    return query
