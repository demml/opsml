from opsml_artifacts.helpers.settings import DefaultSettings
import os


def test_default_local_settings():

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"
    local_client = settings.connection_client
    assert local_client.__class__.__name__ == "LocalSQLConnection"


def test_default_http_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):

    monkeypatch.setenv(name="OPSML_TRACKING_URL", value="https://fake_url.com")
    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"


def test_default_postgres_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    url = "postgresql+psycopg2://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value=url)
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value="gs://opsml/tet")

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"

    assert settings.connection_client.__class__.__name__ == "CloudSqlPostgresql"


def test_default_mysql_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    url = "mysql+pymysql://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    monkeypatch.setenv(name="OPSML_TRACKING_URL", value=url)
    monkeypatch.setenv(name="OPSML_STORAGE_URL", value="gs://opsml/tet")

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"

    assert settings.connection_client.__class__.__name__ == "CloudSqlMySql"


def test_switch_storage_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"

    settings.set_storage_url(storage_url="gs://test")
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"
