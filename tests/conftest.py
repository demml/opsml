import pytest
from opsml_data.helpers.defaults import params
import os
from pathlib import Path


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    try:
        os.remove("gcp_key.json")
    except Exception as e:
        pass

    paths = [path for path in Path(os.getcwd()).rglob("*.csv")]
    for path in paths:
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
