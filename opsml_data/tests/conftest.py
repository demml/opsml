import pytest
from opsml_data.helpers.defaults import defaults
import os


@pytest.fixture(scope="module")
def test_defaults():

    return defaults


@pytest.fixture(scope="module")
def db_name():
    return os.environ.get("DB_NAME")


@pytest.fixture(scope="module")
def db_username():
    return os.environ.get("DB_USERNAME")


@pytest.fixture(scope="module")
def db_password():
    return os.environ.get("DB_PASSWORD")


@pytest.fixture(scope="module")
def db_instance():
    return os.environ.get("DB_INSTANCE_NAME")
