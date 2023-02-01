from opsml_artifacts.helpers.settings import SnowflakeCredentials, Settings
from opsml_artifacts.helpers.models import SnowflakeParams
from unittest.mock import patch


def test_params(test_settings):

    assert issubclass(type(test_settings), Settings)


@patch("opsml_artifacts.helpers.settings.SnowflakeCredentials.credentials")
def test_snowflake_creds(snow_creds, fake_snowflake_params):

    snow_creds.return_value = fake_snowflake_params

    snow_params = SnowflakeCredentials.credentials()
    assert isinstance(snow_params, SnowflakeParams)
    snow_creds.assert_called_once()
