from pydantic import ValidationError
from opsml_data.connector import DataRegistry
from opsml_data.connector.data_model import TestSqlDataRegistrySchema
import sqlalchemy
import pytest


def test_registry_connection(
    test_defaults,
    db_name,
    db_username,
    db_password,
    db_instance,
):

    registry = DataRegistry(
        gcp_project=test_defaults.GCP_PROJECT,
        gcp_region=test_defaults.GCP_REGION,
        instance_name=db_instance,
        db_name=db_name,
        username=db_username,
        password=db_password,
    )

    assert isinstance(registry.engine, sqlalchemy.engine.base.Engine)


def test_list_data(connection, setup_database):
    tables = connection.list_tables()

    assert isinstance(tables, list)


def test_max_version(connection, setup_database):
    version = connection.max_table_version("test_table")
    assert version == 0


def test_insert_data(
    test_data_record,
    test_data_record_wrong,
    connection,
    setup_database,
):
    # this should pass
    connection.insert_data(test_data_record)

    # this should fail
    with pytest.raises(ValidationError) as error:
        connection.insert_data(test_data_record_wrong)
