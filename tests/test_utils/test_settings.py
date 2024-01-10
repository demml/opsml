from opsml.registry.registry import CardRegistries
from opsml.settings.config import OpsmlConfig
from opsml.storage.client import (
    ApiStorageClient,
    GCSFSStorageClient,
    LocalStorageClient,
    S3StorageClient,
    get_storage_client,
)


def test_default_local_settings() -> None:
    cfg = OpsmlConfig(opsml_tracking_uri="sqlite:///test.db", opsml_storage_uri="./mlruns")
    assert isinstance(get_storage_client(cfg=cfg), LocalStorageClient)


def test_default_http_settings(mock_gcs_storage_response, mock_gcp_creds) -> None:
    cfg = OpsmlConfig(opsml_tracking_uri="http://testserver", opsml_storage_uri="gs://google")
    assert isinstance(get_storage_client(cfg=cfg), ApiStorageClient)


def test_default_postgres_settings(mock_gcs_storage_response, mock_gcp_creds) -> None:
    tracking_uri = "postgresql+psycopg2://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    storage_uri = "gs://opsml/test"
    cfg = OpsmlConfig(opsml_tracking_uri=tracking_uri, opsml_storage_uri=storage_uri)
    assert isinstance(get_storage_client(cfg=cfg), GCSFSStorageClient)


def test_default_mysql_settings(mock_aws_storage_response):
    tracking_uri = (
        "mysql+pymysql://test_user:test_password@/ds-test-db?host=/cloudsql/test-project:test-region:test-connection"
    )
    storage_uri = "s3://opsml/test"
    cfg = OpsmlConfig(opsml_tracking_uri=tracking_uri, opsml_storage_uri=storage_uri)
    assert isinstance(get_storage_client(cfg=cfg), S3StorageClient)


def test_api_storage(api_registries: CardRegistries):
    """Tests settings for presence of ApiStorageClient when using api"""
    assert isinstance(api_registries.run._registry.storage_client, ApiStorageClient)
