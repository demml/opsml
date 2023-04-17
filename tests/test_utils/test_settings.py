from opsml.helpers.settings import DefaultSettings
from opsml.registry.storage.types import GcsStorageClientSettings
from opsml.helpers.gcp_utils import GcpCredsSetter
import os


def test_default_local_settings():

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"
    local_client = settings.connection_client
    assert local_client.__class__.__name__ == "LocalSQLConnection"


def test_default_http_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):

    monkeypatch.setenv(name="OPSML_TRACKING_URI", value="https://fake_url.com")
    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"


def test_default_postgres_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    url = "postgresql+psycopg2://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    monkeypatch.setenv(name="OPSML_TRACKING_URI", value=url)
    monkeypatch.setenv(name="OPSML_STORAGE_URI", value="gs://opsml/tet")

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"

    assert settings.connection_client.__class__.__name__ == "CloudSqlPostgresql"


def test_default_mysql_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    url = "mysql+pymysql://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    monkeypatch.setenv(name="OPSML_TRACKING_URI", value=url)
    monkeypatch.setenv(name="OPSML_STORAGE_URI", value="gs://opsml/tet")

    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"

    assert settings.connection_client.__class__.__name__ == "CloudSqlMySql"


def test_switch_storage_settings(monkeypatch, mock_gcs_storage_response, mock_gcp_creds):
    settings = DefaultSettings()
    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"

    gcp_creds = GcpCredsSetter().get_creds()
    storage_settings = GcsStorageClientSettings(
        storage_type="gcs",
        storage_uri="gs://test",
        credentials=gcp_creds.creds,
        gcp_project=gcp_creds.project,
    )

    settings.set_storage(storage_settings=storage_settings)
    assert settings.storage_client.__class__.__name__ == "GCSFSStorageClient"


def test_table_creation(monkeypatch):
    from opsml.helpers.settings import settings

    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"
