from opsml.helpers.gcp_utils import GcpCredsSetter
from opsml.registry.storage.settings import StorageSettings
from opsml.registry.storage.storage_system import (
    ApiStorageClient,
    GCSFSStorageClient,
    LocalStorageClient,
    S3StorageClient,
)
from opsml.registry.storage.types import GcsStorageClientSettings
from opsml.settings.config import OpsmlConfig


def test_default_local_settings() -> None:
    cfg = OpsmlConfig(opsml_tracking_uri="sqlite:///test.db", opsml_storage_uri="./mlruns")
    settings = StorageSettings(cfg=cfg)
    settings.request_client is None
    assert isinstance(settings.storage_client, LocalStorageClient)


def test_default_http_settings(mock_gcs_storage_response, mock_gcp_creds) -> None:
    cfg = OpsmlConfig(opsml_tracking_uri="http://testserver", opsml_storage_uri="gs://google")
    settings = StorageSettings(cfg)

    assert isinstance(settings.storage_client, GCSFSStorageClient)


def test_default_postgres_settings(mock_gcs_storage_response, mock_gcp_creds) -> None:
    tracking_uri = "postgresql+psycopg2://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    storage_uri = "gs://opsml/test"
    cfg = OpsmlConfig(opsml_tracking_uri=tracking_uri, opsml_storage_uri=storage_uri)
    settings = StorageSettings(cfg=cfg)

    assert isinstance(settings.storage_client, GCSFSStorageClient)


def test_default_mysql_settings(mock_aws_storage_response):
    tracking_uri = (
        "mysql+pymysql://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    )
    storage_uri = "s3://opsml/test"
    cfg = OpsmlConfig(opsml_tracking_uri=tracking_uri, opsml_storage_uri=storage_uri)
    settings = StorageSettings(cfg=cfg)

    assert isinstance(settings.storage_client, S3StorageClient)


def test_switch_storage_settings(mock_gcs_storage_response, mock_gcp_creds):
    cfg = OpsmlConfig(opsml_tracking_uri="sqlite:///test.db", opsml_storage_uri="./mlruns")
    settings = StorageSettings(cfg=cfg)

    assert isinstance(settings.storage_client, LocalStorageClient)

    gcp_creds = GcpCredsSetter().get_creds()
    storage_settings = GcsStorageClientSettings(
        storage_type="gcs",
        storage_uri="gs://test",
        credentials=gcp_creds.creds,
        gcp_project=gcp_creds.project,
    )

    settings.storage_settings = storage_settings

    assert isinstance(settings.storage_client, GCSFSStorageClient)


from opsml.registry.sql.registry import CardRegistries


def test_api_storage(api_registries: CardRegistries):
    """Tests settings for presence of ApiStorageClient when using api"""
    assert isinstance(api_registries.run._registry.storage_client, ApiStorageClient)
