from pathlib import Path
from unittest.mock import patch
import pytest
from opsml_artifacts.helpers.request_helpers import ApiClient
from opsml_artifacts.experiments.mlflow_exp import MlFlowExperiment
from opsml_artifacts.experiments.mlflow_helpers import CardRegistries


# need to overwrite the mocked pathlib from root
@pytest.fixture(scope="session", autouse=True)
def mock_pathlib():
    pass


@pytest.fixture(scope="function")
def mock_pyarrow_parquet_write():
    pass


@pytest.fixture(scope="function")
def api_registries(mock_opsml_server):
    """Because settings acts as a singleton,
    we need to explicitly define new card registry types
    in order to test the ClientRegistry functionality
    """

    from tests.test_api.mock_api_registries import CardRegistry

    registries = {}
    for name in ["data", "model", "pipeline", "experiment"]:
        registry = CardRegistry(registry_name=name)
        registry.registry._session = ApiClient(base_url=mock_opsml_server.url)
        registries[name] = registry

    return registries


@pytest.fixture(scope="function")
def mlflow_experiment(mock_opsml_server, api_registries):

    local_url = mock_opsml_server.url
    mlflow_exp = MlFlowExperiment(
        project_name="test_exp",
        team_name="test",
        user_email="test",
        tracking_uri=local_url,
    )

    card_registries = CardRegistries.construct(
        datacard=api_registries["data"],
        modelcard=api_registries["model"],
        experimentcard=api_registries["experiment"],
    )

    mlflow_exp.registries = card_registries

    return mlflow_exp
