from requests import Response
from starlette.testclient import TestClient


def test_opsml_api(monkeypatch):

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
