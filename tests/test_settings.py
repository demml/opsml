from opsml_data.helpers.settings import SnowflakeCredentials, Settings, GCPEnvSetter
from opsml_data.helpers.models import SnowflakeParams


def test_params():

    env_setter = GCPEnvSetter()
    settings = Settings(**env_setter.attributes)
    assert isinstance(settings, Settings)


def test_snowflake_creds():
    snow_creds = SnowflakeCredentials.credentials()

    assert isinstance(snow_creds, SnowflakeParams)
