from opsml_data.helpers.defaults import Defaults, SnowflakeCredentials, params
from opsml_data.helpers.models import Params, SnowflakeParams


def test_defaults():
    defaults_args = Defaults()

    assert isinstance(defaults_args, Defaults)


def test_params():
    assert isinstance(params, Params)


def test_snowflake_creds():
    snow_creds = SnowflakeCredentials.credentials()

    assert isinstance(snow_creds, SnowflakeParams)
