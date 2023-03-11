from requests import Response
from starlette.testclient import TestClient
import os
import pytest
from pytest_lazyfixture import lazy_fixture
from unittest.mock import patch, MagicMock
import pandas as pd
from opsml_artifacts.registry.sql.registry_base import SQLRegistryAPI

# from tests.test_api.server import TestApp


def _test_opsml_get_storage(monkeypatch):

    url = "mysql+pymysql://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value=url)
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value="gs://opsml/test")

    from opsml_artifacts.api.main import opsml_app

    with TestClient(opsml_app) as test_client:
        response: Response = test_client.request(
            method="get",
            url=f"/opsml/storage_path",
        )

        result = response.json()

        assert result.get("storage_type") == "gcs"
        assert result.get("storage_url") == "gs://opsml/test"


def _test_opsml_local_get_storage(monkeypatch):
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value="sqlite://")
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value=None)

    from opsml_artifacts.api.main import opsml_app

    with TestClient(opsml_app) as test_client:
        response: Response = test_client.request(
            method="get",
            url=f"/opsml/storage_path",
        )

        result = response.json()

        assert result.get("storage_type") == "local"


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
    ],
)
def test_register_data(api_registries, test_data, data_splits, mock_pyarrow_parquet_write):

    # create data card
    from opsml_artifacts import DataCard

    registry = api_registries["data"]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )

    # for numpy array
    with patch.multiple("zarr", save=MagicMock(return_value=None)):
        registry.register_card(card=data_card)

        df = registry.list_cards(name=data_card.name, team=data_card.team)
        assert isinstance(df, pd.DataFrame)

        df = registry.list_cards(name=data_card.name)
        assert isinstance(df, pd.DataFrame)

        df = registry.list_cards()
        assert isinstance(df, pd.DataFrame)


def _test_experiment_card(api_registries, linear_regression):
    print(api_registries)
