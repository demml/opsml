import pytest
from opsml_data.helpers.defaults import defaults
from opsml_data.connector.data_model import SqlDataRegistrySchema
from opsml_data.connector import DataRegistry
import os
import pandas as pd
import numpy as np
import pyarrow as pa


@pytest.fixture(scope="session")
def test_defaults():

    return defaults


@pytest.fixture(scope="session")
def db_name():
    return os.environ.get("DB_NAME")


@pytest.fixture(scope="session")
def db_username():
    return os.environ.get("DB_USERNAME")


@pytest.fixture(scope="session")
def db_password():
    return os.environ.get("DB_PASSWORD")


@pytest.fixture(scope="session")
def db_instance():
    return os.environ.get("DB_INSTANCE_NAME")


@pytest.fixture(scope="session")
def connection(
    test_defaults,
    db_instance,
    db_name,
    db_username,
    db_password,
):
    conn = DataRegistry(
        gcp_project=test_defaults.GCP_PROJECT,
        gcp_region=test_defaults.GCP_REGION,
        instance_name=db_instance,
        db_name=db_name,
        username=db_username,
        password=db_password,
        table_name="test_data_registry",
    )

    return conn


@pytest.fixture(scope="session")
def setup_database(connection):

    connection.schema.__table__.create(
        bind=connection.engine,
        checkfirst=True,
    )

    yield

    connection.schema.__table__.drop(bind=connection.engine)


@pytest.fixture(scope="session")
def test_array():
    data = np.arange(10, dtype="int16")
    return data


@pytest.fixture(scope="session")
def test_df():
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2021],
            "n_legs": [2, 4, 5, 100],
            "animals": ["Flamingo", "Horse", "Brittle stars", "Centipede"],
        }
    )

    return df


@pytest.fixture(scope="session")
def test_data_record():
    test_dict = dict(
        table_name="test_table",
        storage_uri="storage_uri_test",
        feature_mapping=dict(col1="int", col2="string"),
        version=1,
        user_email="test_email",
    )

    return test_dict


@pytest.fixture(scope="session")
def test_data_record_wrong():
    test_dict = dict(
        table_name="test_table",
        feature_mapping=dict(col1="int", col2="string"),
        version=0,
        user_email="test_email",
    )

    return test_dict


@pytest.fixture(scope="session")
def test_arrow_table():
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)
    return table
