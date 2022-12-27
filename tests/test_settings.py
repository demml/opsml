from opsml_data.helpers.settings import SnowflakeCredentials, Settings
from opsml_data.helpers.models import SnowflakeParams


def test_params():

    settings = Settings()
    assert isinstance(settings, Settings)


def test_snowflake_creds():
    snow_creds = SnowflakeCredentials.credentials()

    assert isinstance(snow_creds, SnowflakeParams)
