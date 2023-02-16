from opsml_artifacts.registry.sql.connectors import LocalSQLConnection, CloudSQLConnection, SQLConnector
from opsml_artifacts.registry.sql.registry import CardRegistry
import pytest
from unittest.mock import patch, MagicMock


def test_local_connection():
    local_connection = LocalSQLConnection(db_file_path=":memory")
    local_connection.get_engine()


@pytest.mark.parametrize("load_secrets", [True, False])
@pytest.mark.parametrize("db_type", ["postgres", "mysql"])
def test_cloudsql_connection(mock_cloud_sql_connection, load_secrets, mock_gcp_vars, mock_gcp_secrets, db_type):

    cloudsql_connection = mock_cloud_sql_connection(
        db_type=db_type,
        load_from_secrets=load_secrets,
        **mock_gcp_vars,
    )
    cloudsql_connection.get_engine()

    with patch.multiple(
        "google.cloud.sql.connector.Connector",
        connect=MagicMock(return_value=True),
    ):
        assert cloudsql_connection._get_conn()
