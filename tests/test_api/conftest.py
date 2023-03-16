import pytest
import os
from unittest.mock import patch
from starlette.testclient import TestClient
import shutil


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

    from opsml_artifacts.api.main import OpsmlApp

    model_api = OpsmlApp(run_mlflow=True)
    app = model_api.build_app()
    with TestClient(app) as test_client:

        yield test_client

    os.remove(path=tmp_db_path)
    shutil.rmtree("mlruns")


@pytest.fixture(scope="function")
def db_registries(test_app, monkeypatch):
    def callable_api():
        return test_app

    with patch("httpx.Client", callable_api) as mock_registry_api:

        from opsml_artifacts.helpers.settings import settings

        settings.opsml_tracking_uri = "http://testserver"

        from tests.test_api.mock_api_registries import CardRegistry

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
