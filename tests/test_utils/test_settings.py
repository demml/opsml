from opsml_artifacts.helpers.settings import OpsmlSettings


def test_default_local_settings():
    settings = OpsmlSettings()

    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"
    local_client = settings.connection_client

    assert local_client.__class__.__name__ == "LocalSQLConnection"


def test_default_postgres_settings():
    settings = OpsmlSettings()

    assert settings.storage_client.__class__.__name__ == "LocalStorageClient"
