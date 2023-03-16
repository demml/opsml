import pytest
import os

from unittest.mock import patch
from starlette.testclient import TestClient
import shutil
from pathlib import Path


@pytest.fixture(scope="module")
def test_app():

    tmp_db_path = f"{os.path.expanduser('~')}/tmp.db"
    sql_path = f"sqlite:///{tmp_db_path}"

    os.environ["OPSML_TRACKING_URI"] = sql_path
    os.environ["OPSML_STORAGE_URI"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_ARTIFACT_DESTINATION"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_ARTIFACT_ROOT"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_FILE_STORE"] = sql_path
    os.environ["_MLFLOW_SERVER_SERVE_ARTIFACTS"] = "true"

    from opsml_artifacts.app.main import OpsmlApp

    model_api = OpsmlApp(run_mlflow=True)
    app = model_api.build_app()
    with TestClient(app) as test_client:

        yield test_client

    os.remove(path=tmp_db_path)

    try:
        shutil.rmtree("mlruns")
    except Exception as error:
        pass


@pytest.fixture(scope="function")
def db_registries(test_app, monkeypatch):
    def callable_api():
        return test_app

    with patch("httpx.Client", callable_api) as mock_registry_api:

        from opsml_artifacts.helpers.settings import settings

        settings.opsml_tracking_uri = "http://testserver"

        from tests.test_app.mock_api_registries import CardRegistry

        data_registry = CardRegistry(registry_name="data")
        model_registry = CardRegistry(registry_name="model")
        experiment_registry = CardRegistry(registry_name="experiment")
        pipeline_registry = CardRegistry(registry_name="pipeline")

        yield {
            "data": data_registry,
            "model": model_registry,
            "experiment": experiment_registry,
            "pipeline": pipeline_registry,
        }


@pytest.fixture(scope="function")
def mlflow_experiment(db_registries):

    from opsml_artifacts.experiments.mlflow_exp import MlFlowExperiment
    from opsml_artifacts.experiments.mlflow_helpers import CardRegistries

    tmp_db_path = f"{os.path.expanduser('~')}/tmp.db"
    sql_path = f"sqlite:///{tmp_db_path}"
    mlflow_exp = MlFlowExperiment(
        project_name="test_exp",
        team_name="test",
        user_email="test",
        tracking_uri=sql_path,
    )
    mlflow_storage = mlflow_exp._get_storage_client()
    api_card_registries = CardRegistries.construct(
        datacard=db_registries["data"],
        modelcard=db_registries["model"],
        experimentcard=db_registries["experiment"],
    )
    api_card_registries.set_storage_client(mlflow_storage)
    mlflow_exp.registries = api_card_registries
    return mlflow_exp


@pytest.fixture(scope="function")
def mock_pathlib():

    with patch("pathlib.Path", Path) as mocked_pathlib:
        yield mocked_pathlib
