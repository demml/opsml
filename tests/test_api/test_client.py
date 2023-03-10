from requests import Response
from starlette.testclient import TestClient
import requests
import time

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


def test_opsml_local_get_storage(monkeypatch):
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value="sqlite://")
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value="")

    from opsml_artifacts.api.main import opsml_app

    with TestClient(opsml_app) as test_client:
        response: Response = test_client.request(
            method="get",
            url=f"/opsml/storage_path",
        )

        result = response.json()

        assert result.get("storage_type") == "local"
        assert result.get("storage_url") == ":memory:"


def _test_server(monkeypatch, mock_local_conn_server):
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value="sqlite://")
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value="gs://opsml/test")
    from tests.test_api.server import TestApp

    app = TestApp()
    app.start()
    #
    # response = requests.get(f"{app.url}/opsml/healthcheck")
    # assert response.json()["is_alive"] == True
    #
    # app.shutdown()
