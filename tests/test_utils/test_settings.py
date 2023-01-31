from opsml_artifacts.helpers.settings import SnowflakeCredentials, GlobalSettings
from opsml_artifacts.helpers.models import SnowflakeParams


def test_params():

    settings = GlobalSettings()

    assert isinstance(settings, GlobalSettings)


def test_snowflake_creds():
    snow_creds = SnowflakeCredentials.credentials()

    assert isinstance(snow_creds, SnowflakeParams)
