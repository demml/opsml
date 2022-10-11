from opsml_data.connector import DataRegistry
import sqlalchemy


def test_registry_connection(
    test_defaults, db_name, db_username, db_password, db_instance
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


def test_list_tables(test_defaults, db_name, db_username, db_password, db_instance):
    registry = DataRegistry(
        gcp_project=test_defaults.GCP_PROJECT,
        gcp_region=test_defaults.GCP_REGION,
        instance_name=db_instance,
        db_name=db_name,
        username=db_username,
        password=db_password,
    )

    tables = registry.list_data_tables()

    assert isinstance(tables, list)
