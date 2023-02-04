from opsml_artifacts.registry.sql.connectors import LocalSQLConnection, CloudSQLConnection
import pytest


def test_local_connection():
    local_connection = LocalSQLConnection(db_file_path=":memory")
    local_connection.get_engine()


@pytest.mark.parametrize("load_secrets", [True, False])
def test_cloudsql_connection(db_registries, load_secrets, mock_gcp_vars, mock_gcp_secrets):

    cloudsql_connection = CloudSQLConnection(
        load_from_secrets=load_secrets,
        db_type="mysql",
        **mock_gcp_vars,
    )
    cloudsql_connection.get_engine()
